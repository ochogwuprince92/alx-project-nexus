
from rest_framework import viewsets, permissions, generics, status
from .models import JobApplication, Notification
from .serializers import JobApplicationSerializer, NotificationSerializer, JobApplicationStatusUpdateSerializer
from .tasks import send_application_email_task
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Attach the logged-in user to the application
        application = serializer.save(user=self.request.user)

        # Send email async
        job = application.job
        subject = f"New Application for {job.title}"
        message = f"{application.user.email} applied for {job.title}."

        # Notification
        if job.posted_by:  # safety check
            Notification.objects.create(
                recipient=job.posted_by,
                message=message
            )

        recipient = job.company_name  # might replace with email
        send_application_email_task.delay(recipient, subject, message)
    
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Notification.objects.none()  # avoid crash
        return Notification.objects.filter(recipient=user).order_by("-created_at")    

class JobApplicationStatusUpdateView(generics.UpdateAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        application = serializer.save()

        # In-app notification
        message = f"Your application for '{application.job.title}' has been {application.status}."
        if application.user:  # safety
            Notification.objects.create(
                recipient=application.user,
                message=message
            )

        # Async email
        subject = f"Application Status Updated: {application.job.title}"
        email_message = f"Hello {application.user.email},\n\n{message}\n\nPlease log in to view more details."
        send_application_email_task.delay(application.user.email, subject, email_message)
    
class UserJobApplicationsListView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return JobApplication.objects.none()
        return JobApplication.objects.filter(user=user).order_by("-applied_at")

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
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        notification = Notification.objects.filter(pk=kwargs['pk'], recipient=user).first()
        if not notification:
            return Response({"detail": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

        notification.is_read = True
        notification.save()
        return Response({"detail": "Notification marked as read"}, status=status.HTTP_200_OK)
