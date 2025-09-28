from rest_framework import viewsets, permissions, generics, status
from .models import JobApplication, Notification
from .serializers import (
    JobApplicationSerializer,
    NotificationSerializer,
    JobApplicationStatusUpdateSerializer,
)
from .tasks import send_application_email_task
from django.core.mail import send_mail
import logging
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import os
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from django.utils.encoding import iri_to_uri
from .permissions import IsJobPosterOrAdmin


class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="List job applications for the current filter/view.",
        security=[{"Bearer": []}],
    )
    def list(self, request, *args, **kwargs):
        # Cache list responses; include user id to avoid leaking others' data
        user_part = (
            f":user={request.user.pk}"
            if request.user and request.user.is_authenticated
            else ""
        )
        key = f"applications:list:{iri_to_uri(request.get_full_path())}{user_part}"
        cached = cache.get(key)
        if cached is not None:
            return cached

        response = super().list(request, *args, **kwargs)
        try:
            cache.set(key, response, timeout=30)
        except Exception:
            pass
        return response

    def perform_create(self, serializer):
        # Attach the logged-in user to the application and perform post-create actions
        application = serializer.save(user=self.request.user)

        # Post-create: send in-app notification and an async email to the job poster/company
        job = getattr(application, "job", None)
        if not job:
            return

        # Build message
        job_title = getattr(job, "title", "the job")
        user = getattr(application, "user", None)
        user_email = getattr(user, "email", None)
        # Prefer email, then phone, then first_name, then fallback
        user_display = (
            user_email
            or getattr(user, "phone", None)
            or getattr(user, "first_name", None)
            or "A user"
        )
        subject = f"New Application for {job_title}"
        message = f"{user_display} applied for {job_title}."

        # In-app notification to the poster, if any
        posted_by = getattr(job, "posted_by", None)
        if posted_by:
            Notification.objects.create(recipient=posted_by, message=message)

        # Choose an email recipient: poster's email -> job.company_email -> fallback to company_name
        recipient = None
        if posted_by and getattr(posted_by, "email", None):
            recipient = posted_by.email
        elif getattr(job, "company_email", None):
            recipient = job.company_email
        else:
            recipient = getattr(job, "company_name", None)

        # Fire-and-forget async email (validate recipient first; don't let failures break the request)
        logger = logging.getLogger(__name__)
        try:
            # Only send if recipient is a valid email address
            validate_email(recipient)
            # Use Celery if broker is available; otherwise call synchronously in eager mode
            if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
                send_application_email_task(recipient, subject, message)
            else:
                send_application_email_task.delay(recipient, subject, message)
        except (ValidationError, TypeError):
            # recipient isn't a valid email (could be company_name or None)
            # If we have a company_name, send a fallback email to DEFAULT_FROM_EMAIL and include intended recipient
            company_name = getattr(job, "company_name", None)
            if company_name:
                fallback = getattr(settings, "DEFAULT_FROM_EMAIL", None)
                if fallback:
                    fallback_message = (
                        f"[Intended recipient: {company_name}]\n\n{message}"
                    )
                    try:
                        if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
                            send_application_email_task(fallback, subject, fallback_message)
                        else:
                            send_application_email_task.delay(
                                fallback, subject, fallback_message
                            )
                        logger.info(
                            "Sent fallback email to %s for company %s (job=%s)",
                            fallback,
                            company_name,
                            getattr(job, "id", None),
                        )
                    except Exception:
                        logger.exception(
                            "Failed to enqueue fallback send_application_email_task for fallback=%r",
                            fallback,
                        )
                else:
                    logger.warning(
                        "No DEFAULT_FROM_EMAIL configured; skipping email for company=%r",
                        company_name,
                    )
            else:
                logger.warning(
                    "Skipping email send: invalid recipient=%r for job=%r",
                    recipient,
                    getattr(job, "id", None),
                )
        except Exception:
            # If Celery task enqueue fails, we silently continue so the API response isn't affected
            logger.exception(
                "Failed to enqueue send_application_email_task for recipient=%r",
                recipient,
            )
        finally:
            # Invalidate simple application-related caches
            try:
                if hasattr(cache, "delete_pattern"):
                    cache.delete_pattern("applications:list:*")
                    cache.delete_pattern("notifications:list:*")
                    cache.delete_pattern("user_applications:list:*")
                else:
                    cache.clear()
            except Exception:
                pass

    @swagger_auto_schema(
        operation_description="Create a new job application",
        security=[{"Bearer": []}],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List notifications for the authenticated user",
        security=[{"Bearer": []}],
    )
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Notification.objects.none()  # avoid crash
        return Notification.objects.filter(recipient=user).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        # Cache per-user notification list briefly
        if not request.user or not request.user.is_authenticated:
            return super().list(request, *args, **kwargs)
        key = f"notifications:list:user={request.user.pk}:{iri_to_uri(request.get_full_path())}"
        cached = cache.get(key)
        if cached is not None:
            return cached

        response = super().list(request, *args, **kwargs)
        try:
            cache.set(key, response, timeout=15)
        except Exception:
            pass
        return response


class JobApplicationStatusUpdateView(generics.UpdateAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsJobPosterOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = JobApplication.objects.all()
        # Non-admins can only access applications for jobs they posted
        if not (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)):
            qs = qs.filter(job__posted_by=user)
        return qs

    @swagger_auto_schema(
        operation_description="Update job application status (job poster or admin)",
        security=[{"Bearer": []}],
    )
    def perform_update(self, serializer):
        application = serializer.save()

        # In-app notification
        message = f"Your application for '{application.job.title}' has been {application.status}."
        if application.user:  # safety
            Notification.objects.create(recipient=application.user, message=message)

        # Async email (use direct email of the user)
        subject = f"Application Status Updated: {application.job.title}"
        to_email = getattr(application.user, "email", None)
        email_message = f"Hello {to_email},\n\n{message}\n\nPlease log in to view more details."
        if to_email:
            # In tests, avoid Celery to prevent backend import issues
            if getattr(settings, "DJANGO_TESTING", None) or os.getenv("DJANGO_TESTING") == "1":
                try:
                    send_mail(subject, email_message, settings.EMAIL_HOST_USER, [to_email], fail_silently=True)
                except Exception:
                    pass
            else:
                # Use Celery in non-test environments; if eager, call synchronously
                if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
                    send_application_email_task(to_email, subject, email_message)
                else:
                    send_application_email_task.delay(to_email, subject, email_message)

        # Invalidate related caches
        try:
            if hasattr(cache, "delete_pattern"):
                cache.delete_pattern("applications:list:*")
                cache.delete_pattern("notifications:list:*")
                cache.delete_pattern("user_applications:list:*")
            else:
                cache.clear()
        except Exception:
            pass


class UserJobApplicationsListView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return JobApplication.objects.none()
        return (
            JobApplication.objects.filter(user=self.request.user)
            .select_related("job")
            .order_by("-applied_at")
        )

    def list(self, request, *args, **kwargs):
        # Cache per-user job applications list
        if not request.user or not request.user.is_authenticated:
            return super().list(request, *args, **kwargs)
        key = f"user_applications:list:user={request.user.pk}:{iri_to_uri(request.get_full_path())}"
        cached = cache.get(key)
        if cached is not None:
            return cached

        response = super().list(request, *args, **kwargs)
        try:
            cache.set(key, response, timeout=20)
        except Exception:
            pass
        return response


class MarkNotificationReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Notification.objects.none()
        return Notification.objects.filter(recipient=user)

    def patch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        notification = Notification.objects.filter(
            pk=kwargs["pk"], recipient=user
        ).first()
        if not notification:
            return Response(
                {"detail": "Notification not found"}, status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.save()
        return Response(
            {"detail": "Notification marked as read"}, status=status.HTTP_200_OK
        )