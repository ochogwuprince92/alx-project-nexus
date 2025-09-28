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
# Reset the testing flag so production settings apply below
os.environ["DJANGO_TESTING"] = "0"

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

    

    # Email: prefer console unless SMTP creds are provided or forced
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@example.com")

    EMAIL_FORCE_SMTP = config("EMAIL_FORCE_SMTP", default=False, cast=bool)
    _has_smtp_creds = bool(EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)
    if EMAIL_FORCE_SMTP or _has_smtp_creds:
        EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    else:
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # Celery: if no broker configured, run tasks eagerly (synchronously)
    _broker = config("CELERY_BROKER_URL", default="")
    if _broker:
        CELERY_BROKER_URL = _broker
        CELERY_RESULT_BACKEND = config(
            "CELERY_RESULT_BACKEND", default=_broker
        )
        CELERY_TASK_ALWAYS_EAGER = False
    else:
        CELERY_BROKER_URL = None
        CELERY_RESULT_BACKEND = None
        CELERY_TASK_ALWAYS_EAGER = True
        CELERY_TASK_EAGER_PROPAGATES = True

    # Cache: use Redis only if REDIS_CACHE_URL is provided, else LocMem for free tier
    REDIS_CACHE_URL = config("REDIS_CACHE_URL", default="")
    if REDIS_CACHE_URL:
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": REDIS_CACHE_URL,
                "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            }
        }
    else:
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "prod-freetier-cache",
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
