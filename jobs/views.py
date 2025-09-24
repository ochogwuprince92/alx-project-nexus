from rest_framework import viewsets, permissions, generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Job, CompanyProfile, JobCategory, JobTag
from .serializers import (
    JobSerializer,
    CompanyProfileSerializer,
    JobCategorySerializer,
    JobTagSerializer,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.cache import cache
from django.utils.encoding import iri_to_uri


# Jobs
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().select_related("category").prefetch_related("tags")
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["employment_type", "location", "category", "tags"]
    search_fields = ["title", "description", "requirements", "company_name"]
    ordering_fields = ["created_at", "salary_min"]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)
        # Invalidate job list cache (simple approach: clear keys with prefix)
        try:
            # Using cache.delete_pattern if available (django-redis); fallback to clearing entire cache
            if hasattr(cache, "delete_pattern"):
                cache.delete_pattern("jobs:list:*")
            else:
                # Best-effort: clear the whole default cache
                cache.clear()
        except Exception:
            pass

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            if hasattr(cache, "delete_pattern"):
                cache.delete_pattern("jobs:list:*")
            else:
                cache.clear()
        except Exception:
            pass

    def perform_destroy(self, instance):
        instance.delete()
        try:
            if hasattr(cache, "delete_pattern"):
                cache.delete_pattern("jobs:list:*")
            else:
                cache.clear()
        except Exception:
            pass

    def list(self, request, *args, **kwargs):
        """Cache list responses based on path and query params for a short TTL."""
        # Build a cache key from the full path (includes querystring)
        key = f"jobs:list:{iri_to_uri(request.get_full_path())}"
        cached = cache.get(key)
        if cached is not None:
            return cached

        response = super().list(request, *args, **kwargs)
        # Cache for 30 seconds by default
        try:
            cache.set(key, response, timeout=30)
        except Exception:
            # Silently ignore cache errors
            pass

        return response


# Companies
class CompanyProfileViewSet(viewsets.ModelViewSet):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Categories
class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.AllowAny]


# Tags
class JobTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobTag.objects.all()
    serializer_class = JobTagSerializer
    permission_classes = [permissions.AllowAny]
