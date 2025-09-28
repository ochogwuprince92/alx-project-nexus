import os
# Prevent base settings from requiring POSTGRES_* at import time
# by forcing the sqlite branch; we'll override DATABASES below.
os.environ.setdefault("DJANGO_TESTING", "1")

from .settings import *  # noqa: F401,F403
from decouple import config, Csv
import dj_database_url

# ---------------------
# Production overrides
# ---------------------
DEBUG = False

# Never run tests in production accidentally
if os.environ.get("DJANGO_TESTING") == "1":
    # Instead of raising an error, just switch to test DB and console email
    from backend.ci_settings import *
else:
    # Require SECRET_KEY in production
    SECRET_KEY = config("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be set in environment for production")

    # ALLOWED_HOSTS should be explicitly provided
    ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="", cast=Csv())

    # Prefer DATABASE_URL if provided by the platform (Render blueprint databases)
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        DATABASES = {
            "default": dj_database_url.parse(db_url, conn_max_age=600, ssl_require=False)
        }
    else:
        # PostgreSQL via individual env vars
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": config("POSTGRES_DB"),
                "USER": config("POSTGRES_USER"),
                "PASSWORD": config("POSTGRES_PASSWORD"),
                "HOST": config("POSTGRES_HOST"),
                "PORT": config("POSTGRES_PORT", cast=int),
            }
        }

    

    # Email
    EMAIL_BACKEND = config(
        "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
    )
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@example.com")

    # Celery
    CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = config(
        "CELERY_RESULT_BACKEND", default="redis://localhost:6379/0"
    )

    # Redis cache
    REDIS_CACHE_URL = config("REDIS_CACHE_URL", default="redis://localhost:6379/1")
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_CACHE_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }

# Security headers
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# Minimal console logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
