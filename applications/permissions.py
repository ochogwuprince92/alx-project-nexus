from common.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly  # re-export for convenience
from rest_framework.permissions import BasePermission

from .models import JobApplication

__all__ = [
    "IsOwnerOrReadOnly",
    "IsAdminOrReadOnly",
    "IsJobPosterOrAdmin",
]


class IsJobPosterOrAdmin(BasePermission):
    """Allow access if the user is staff/admin or is the poster of the job for the application.

    Intended for object-level checks on `JobApplication` instances.
    """

    def has_permission(self, request, view):
        # Require authentication at minimum; view can stack IsAuthenticated as well
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Safety: ensure we're checking against a JobApplication instance
        if not isinstance(obj, JobApplication):
            return False

        user = request.user
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return True

        # Poster can act on applications to their job
        try:
            return getattr(obj.job, "posted_by_id", None) == getattr(user, "id", None)
        except Exception:
            return False
