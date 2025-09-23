
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
        message = f"{application.user.username} applied for {job.title}."
        Notification.objects.create(
            recipient=job.posted_by,
            message=message
        )

        recipient = job.company_name  # you might replace this with job.company.email

        send_application_email_task.delay(recipient, subject, message)
    
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")
    
class JobApplicationStatusUpdateView(generics.UpdateAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        application = serializer.save()

        # Send in-app notification
        message = f"Your application for '{application.job.title}' has been {application.status}."
        Notification.objects.create(
            recipient=application.user,
            message=message
        )

        # Send async email
        subject = f"Application Status Updated: {application.job.title}"
        email_message = f"Hello {application.user.username},\n\n{message}\n\nPlease log in to view more details."
        send_application_email_task.delay(application.user.email, subject, email_message)
    
class UserJobApplicationsListView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user).order_by("-applied_at")

class MarkNotificationReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        notification = Notification.objects.get(pk=kwargs['pk'], recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({"detail": "Notification marked as read"}, status=status.HTTP_200_OK)