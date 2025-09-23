from rest_framework.routers import DefaultRouter
from .views import JobViewSet, CompanyProfileViewSet, JobCategoryViewSet, JobTagViewSet

router = DefaultRouter()
router.register(r"jobs", JobViewSet, basename="job")
router.register(r"companies", CompanyProfileViewSet, basename="company")
router.register(r"categories", JobCategoryViewSet, basename="category")
router.register(r"tags", JobTagViewSet, basename="tag")

urlpatterns = router.urls
