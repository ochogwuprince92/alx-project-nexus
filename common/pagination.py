from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """A sensible default pagination class for API endpoints.

    - Default page size: 10
    - Allows clients to request a custom page size with `?page_size=` up to max_page_size
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
