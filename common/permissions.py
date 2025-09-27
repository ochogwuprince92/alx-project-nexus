from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """Allow read-only for everyone; write only for the owner.

    Expects model instances to have a `user` attribute pointing to the owner.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "user", None)
        return owner == getattr(request, "user", None)


class IsAdminOrReadOnly(BasePermission):
    """Allow read-only for everyone; write for staff/admin users only."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = getattr(request, "user", None)
        return bool(user and (user.is_staff or user.is_superuser))
