from rest_framework import serializers
from .models import Job, CompanyProfile, JobCategory, JobTag
from django.contrib.auth import get_user_model

User = get_user_model()

class JobSerializer(serializers.ModelSerializer):
    # Make relations optional and friendly to Swagger's default "0" inputs
    company = serializers.PrimaryKeyRelatedField(
        queryset=CompanyProfile.objects.all(), required=False, allow_null=True
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=JobCategory.objects.all(), required=False, allow_null=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=JobTag.objects.all(), many=True, required=False
    )

    class Meta:
        model = Job
        fields = "__all__"
        ref_name = "JobSerializer_Custom"  # avoid Swagger conflicts
        extra_kwargs = {
            # Server sets posted_by in the view; do not require it in requests
            "posted_by": {"read_only": True},
            # Make relations optional (reflected in schema/Swagger)
            "company": {"required": False, "allow_null": True},
            "category": {"required": False, "allow_null": True},
            "tags": {"required": False},
        }

    def to_internal_value(self, data):
        # Make a shallow copy we can mutate safely
        data = data.copy() if isinstance(data, dict) else data

        # Remove posted_by if a client sends it; it's read-only and set server-side
        if isinstance(data, dict) and "posted_by" in data:
            data.pop("posted_by", None)

        # Coerce common UI defaults of '0' / 0 to None for optional FKs
        for fk in ("company", "category"):
            if isinstance(data, dict) and fk in data and data.get(fk) in ("0", 0, ""):
                data[fk] = None

        # Coerce tags: if '0'/0 provided, drop it; if tags is '0', make it []
        if isinstance(data, dict) and "tags" in data:
            raw_tags = data.get("tags")
            if raw_tags in ("0", 0, ""):
                data["tags"] = []
            elif isinstance(raw_tags, list):
                data["tags"] = [t for t in raw_tags if t not in ("0", 0, "")]

        return super().to_internal_value(data)

    def validate(self, attrs):
        # Coerce string/integer 0 to None for optional FKs commonly sent by UIs
        for fk in ("company", "category"):
            if fk in self.initial_data and self.initial_data.get(fk) in ("0", 0):
                attrs[fk] = None
        # Coerce tags [0] or "0" to empty list
        if "tags" in self.initial_data:
            raw_tags = self.initial_data.get("tags")
            if raw_tags in ("0", 0):
                attrs["tags"] = []
            elif isinstance(raw_tags, list) and any(t in ("0", 0) for t in raw_tags):
                attrs["tags"] = [t for t in raw_tags if t not in ("0", 0)]
        return super().validate(attrs)

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = "__all__"
        ref_name = "CompanyProfileSerializer_Custom"

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = "__all__"
        ref_name = "JobCategorySerializer_Custom"

class JobTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTag
        fields = "__all__"
        ref_name = "JobTagSerializer_Custom"
