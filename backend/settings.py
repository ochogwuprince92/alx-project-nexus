import os
from decouple import config, Csv
from datetime import timedelta
from pathlib import Path

# ---------------------
# Basic Paths
# ---------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------
# Secret & Debug
# ---------------------
SECRET_KEY = config("DJANGO_SECRET_KEY", default="test-secret")
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="*", cast=Csv())

WSGI_APPLICATION = "backend.wsgi.application"
ROOT_URLCONF = "backend.urls"

# ---------------------
# Installed Apps (add users and jobs apps)
# ---------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "applications",
    "users",
    "jobs",
    "common",
    "drf_spectacular",
    "drf_yasg",
]

# ---------------------
# Middleware
# ---------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------
# Database (PostgreSQL)
# ---------------------
if os.environ.get("DJANGO_TESTING") == "1":
    # Use a lightweight sqlite DB for local test runs
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test_db.sqlite3",
        }
    }
else:
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

# ---------------------
# Authentication
# ---------------------
AUTH_USER_MODEL = "users.User"

# Use custom backend that supports email or phone login, with default ModelBackend fallback
AUTHENTICATION_BACKENDS = [
    "users.auth_backends.PhoneOrEmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ---------------------
# REST Framework & JWT
# ---------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 10,
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "1000/day",
        "anon": "100/day",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("ACCESS_TOKEN_LIFETIME_MINUTES", default=15, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("REFRESH_TOKEN_LIFETIME_DAYS", default=1, cast=int)
    ),
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# ---------------------
# Email (SMTP)
# ---------------------
# Configure SMTP in base so local/dev sends real emails when credentials are supplied
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@nexusjobboard.com")

# ---------------------
# Static & Media
# ---------------------
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------
# Other settings
# ---------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_L10N = True
USE_TZ = True

SPECTACULAR_SETTINGS = {
    "TITLE": "Nexus Job Board API",
    "DESCRIPTION": "Backend API for job seekers and employers",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# drf-yasg Swagger UI settings: define Bearer token security and disable session auth in UI
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {your token}'",
        }
    },
    "USE_SESSION_AUTH": False,
}

# Silence drf-yasg compatibility warning about renderers
SWAGGER_USE_COMPAT_RENDERERS = False

# Email config (for dev use console backend)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@nexusjobboard.com"

REST_FRAMEWORK.update(
    {
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.UserRateThrottle",
            "rest_framework.throttling.AnonRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {
            "user": "1000/day",  # logged-in users
            "anon": "100/day",  # anonymous users
        },
    }
)

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Africa/Lagos"

# ---------------------
# Caching (use local memory for tests, Redis for dev/prod)
# ---------------------
DEFAULT_CACHE_ALIAS = "default"
if os.environ.get("DJANGO_TESTING") == "1":
    CACHES = {
        DEFAULT_CACHE_ALIAS: {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
else:
    # Use django-redis if available; fall back to simple backend if not installed
    try:
        CACHES = {
            DEFAULT_CACHE_ALIAS: {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": config(
                    "REDIS_CACHE_URL", default="redis://localhost:6379/1"
                ),
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                },
            }
        }
    except Exception:
        CACHES = {
            DEFAULT_CACHE_ALIAS: {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "fallback-cache",
            }
        }
