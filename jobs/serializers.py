from rest_framework import serializers
from .models import Job, CompanyProfile, JobCategory, JobTag
from django.contrib.auth import get_user_model

User = get_user_model()

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"
        ref_name = "JobSerializer_Custom"  # avoid Swagger conflicts

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
