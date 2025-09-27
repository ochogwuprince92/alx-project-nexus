from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from typing import Optional


class PhoneOrEmailBackend(BaseBackend):
    """Authenticate with either email or phone plus password.

    Accepts kwargs: email, phone, password. Falls back to username -> email.
    """

    def authenticate(self, request, email: Optional[str] = None, phone: Optional[str] = None,
                     password: Optional[str] = None, **kwargs):
        User = get_user_model()
        user = None

        # Fallback: some clients send 'username' instead of email
        if not email and not phone and "username" in kwargs:
            email = kwargs.get("username")

        try:
            if email:
                user = User.objects.filter(email=email).first()
            elif phone:
                user = User.objects.filter(phone=phone).first()
        except Exception:
            return None

        if not user or not password:
            return None

        if user.check_password(password) and user.is_active:
            return user
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
