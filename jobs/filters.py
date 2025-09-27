import django_filters
from .models import Job


class JobFilter(django_filters.FilterSet):
    """Filters for the Job model used by JobViewSet.

    Supports filtering by:
    - employment_type (exact)
    - location (icontains)
    - category (by id)
    - tags (by id; many-to-many)
    - salary_min (gte/lte range)
    - salary_max (gte/lte range)
    - created_at (date range)
    - has_deadline (boolean, derived)
    """

    location = django_filters.CharFilter(field_name="location", lookup_expr="icontains")
    category = django_filters.NumberFilter(field_name="category__id", lookup_expr="exact")
    tags = django_filters.NumberFilter(field_name="tags__id", lookup_expr="exact")

    salary_min_gte = django_filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    salary_min_lte = django_filters.NumberFilter(field_name="salary_min", lookup_expr="lte")
    salary_max_gte = django_filters.NumberFilter(field_name="salary_max", lookup_expr="gte")
    salary_max_lte = django_filters.NumberFilter(field_name="salary_max", lookup_expr="lte")

    created_at_after = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")

    has_deadline = django_filters.BooleanFilter(method="filter_has_deadline")

    class Meta:
        model = Job
        fields = [
            "employment_type",
            "location",
            "category",
            "tags",
            "salary_min_gte",
            "salary_min_lte",
            "salary_max_gte",
            "salary_max_lte",
            "created_at_after",
            "created_at_before",
            "has_deadline",
        ]

    def filter_has_deadline(self, queryset, name, value):
        if value is True:
            return queryset.exclude(deadline__isnull=True)
        if value is False:
            return queryset.filter(deadline__isnull=True)
        return queryset

