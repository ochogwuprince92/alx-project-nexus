from .models import JobApplication, Notification
from rest_framework import serializers

class JobApplicationSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    job_title = serializers.ReadOnlyField(source="job.title")

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "job",
            "job_title",
            "user",         # can keep it read-only
            "user_email",
            "cover_letter",
            "resume",
            "status",
            "applied_at"
        ]
        read_only_fields = ["status", "applied_at", "user", "user_email", "job_title"]
    def validate(self, data):
        user = self.context["request"].user
        job = data.get("job")

        if JobApplication.objects.filter(user=user, job=job).exists():
            raise serializers.ValidationError("You have already applied to this job.")

        return data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "message", "is_read", "created_at"]

class JobApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ["status"]

    def validate_status(self, value):
        if value not in ["pending", "accepted", "rejected"]:
            raise serializers.ValidationError("Invalid status.")
        return value