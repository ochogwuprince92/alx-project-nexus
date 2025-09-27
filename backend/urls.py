from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Nexus Job Board API",
        default_version="v1",
        description="API documentation for the Nexus Job Board backend",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@nexus.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/jobs/", include("jobs.urls")),
    path("api/applications/", include("applications.urls")),
    # Swagger & Redoc
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("openapi/", schema_view.without_ui(cache_timeout=0), name="schema-openapi"),
]
