Deployment checklist & commands
===============================

This file documents a minimal, repeatable process to deploy the Nexus Job Board backend to a Linux server. Customize as needed for Docker, Kubernetes or your preferred hosting.

Required environment variables (must be set for production):

- DJANGO_SETTINGS_MODULE=backend.production_settings
- DJANGO_SECRET_KEY — a long random secret
- DJANGO_DEBUG=False
- DJANGO_ALLOWED_HOSTS — comma-separated hostnames
- POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
- CELERY_BROKER_URL, CELERY_RESULT_BACKEND (e.g., redis://redis:6379/0)
- EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
- DEFAULT_FROM_EMAIL

Server setup (example using virtualenv + systemd)

1. Create virtualenv and install requirements

    python3 -m venv /opt/nexus/.venv
    source /opt/nexus/.venv/bin/activate
    pip install -r /path/to/alx-project-nexus/requirements.txt

2. Environment variables

   Use your process manager or systemd drop-in to export environment variables for the service.

3. Database migrations & static files

    /opt/nexus/.venv/bin/python /path/to/alx-project-nexus/manage.py migrate --noinput
    /opt/nexus/.venv/bin/python /path/to/alx-project-nexus/manage.py collectstatic --noinput

4. Start Gunicorn (example systemd service)

    ExecStart=/opt/nexus/.venv/bin/gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 3

5. Start Celery workers (systemd or supervisor)

    /opt/nexus/.venv/bin/celery -A backend.celery worker --loglevel=info

Health checks & smoke tests

After deployment run a few smoke checks:

    curl -I https://your.domain/swagger/
    curl -I https://your.domain/api/jobs/

Rollback plan

- Keep a tag for each release. To rollback, checkout the previous tag and re-deploy.
- For destructive migrations, plan a migration rollback or use feature flags.

Notes

- Do NOT set DJANGO_TESTING in production — it switches to an sqlite DB.
- Ensure SECRET_KEY and email credentials are kept secret and provided via a secrets manager or environment variables.
