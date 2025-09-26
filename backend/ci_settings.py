from .settings import *

# -----------------------
# Testing environment
# -----------------------
DEBUG = True
DJANGO_TESTING = "1"

# Use SQLite for tests to avoid Postgres dependency in unit tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

# Use console email backend for testing
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Fake secret key for CI (no need to expose production secret)
SECRET_KEY = "ci-secret-key"

# Use local memory cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ci-cache",
    }
}

# Celery uses Redis as usual
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
