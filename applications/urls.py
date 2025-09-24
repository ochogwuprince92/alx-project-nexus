from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobApplicationViewSet, 
    NotificationListView, 
    JobApplicationStatusUpdateView,
    UserJobApplicationsListView,
    MarkNotificationReadView
)

router = DefaultRouter()
router.register(r"", JobApplicationViewSet, basename="job-application")

urlpatterns = [
    path("", include(router.urls)),  # Default CRUD for applications
    path("my/", UserJobApplicationsListView.as_view(), name="user-applications"),  # Custom: user’s own applications
    path("notifications/", NotificationListView.as_view(), name="notifications"),  # List notifications
    path("applications/<int:pk>/status/", JobApplicationStatusUpdateView.as_view(), name="application-status-update"),  # Update status
    path("notifications/<int:pk>/read/", MarkNotificationReadView.as_view(), name="mark-notification-read"),  # Mark read
]
