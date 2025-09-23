from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobApplicationViewSet, NotificationListView, JobApplicationStatusUpdateView, MarkNotificationReadView

router = DefaultRouter()
router.register(r"applications", JobApplicationViewSet, basename="job-application")

urlpatterns = [
    path("", include(router.urls)),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("applications/<int:pk>/status/", JobApplicationStatusUpdateView.as_view(), name="application-status-update"),
    path("my-applications/", include("applications.views.UserJobApplicationsListView"), name="user-applications"),
    path('notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
]
