from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from jobs.models import Job

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    cover_letter = models.TextField(blank=True, null=True)
    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["pdf"])],
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["job", "user"], name="unique_job_application")
        ]
        ordering = ["-applied_at"]
        verbose_name_plural = "Job Applications"

    def __str__(self):
        user_ident = getattr(self.user, "email", None) or getattr(self.user, "phone", None) or f"user-{self.user_id}"
        return f"{user_ident} applied to {self.job.title}"

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient} - {self.message[:30]}"

    class Meta:
        verbose_name_plural = "Notifications"