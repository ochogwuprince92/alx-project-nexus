try:
    from .celery import app as celery_app
except Exception:
    # Celery may not be installed in lightweight test environments.
    celery_app = None

__all__ = ["celery_app"]
