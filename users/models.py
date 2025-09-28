from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import uuid

class UserManager(BaseUserManager):
    """Custom user manager to handle user creation with email or phone"""
    def create_user(self, email=None, phone=None, password=None, **extra_fields):
        if not email and not phone:
            raise ValueError("Users must provide either email or phone")
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with email/phone login and role"""
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
    )
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Verification status
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or self.phone or f"user-{self.pk}"

    def get_full_name(self):
        full = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full or (self.email or self.phone or "")
    
# EmailToken for Signup Verification
class EmailToken(models.Model):
    PURPOSE_SIGNUP = "signup"
    PURPOSE_CHOICES = [
        (PURPOSE_SIGNUP, "Signup verification"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_tokens")
    token = models.CharField(max_length=64, unique=True)
    purpose = models.CharField(max_length=12, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} - {self.purpose}"

    @classmethod
    def create_for_user(cls, user, purpose, ttl_hours=24):
        import secrets
        token = secrets.token_urlsafe(32)  # long secure token
        expires_at = timezone.now() + timezone.timedelta(hours=ttl_hours)
        return cls.objects.create(user=user, purpose=purpose, token=token, expires_at=expires_at)

    def is_valid(self):
        return timezone.now() <= self.expires_at

# EmailOTP for Password Reset
class EmailOTP(models.Model):
    PURPOSE_RESET = "reset"
    PURPOSE_CHOICES = [
        (PURPOSE_RESET, "Password reset"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_otps")
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=12, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user", "purpose", "code"]),
            models.Index(fields=["expires_at"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["user", "purpose", "code"], name="unique_user_purpose_code")
        ]

    def __str__(self):
        return f"{self.user.email} - {self.purpose} - {self.code}"

    @classmethod
    def create_for_user(cls, user, purpose, ttl_minutes=10, code_generator=None):
        import random
        code = code_generator() if code_generator else f"{random.randint(0, 999999):06d}"
        expires_at = timezone.now() + timezone.timedelta(minutes=ttl_minutes)
        return cls.objects.create(user=user, purpose=purpose, code=code, expires_at=expires_at)

    def is_valid(self):
        return (not self.used) and (timezone.now() <= self.expires_at)
