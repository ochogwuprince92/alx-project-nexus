#!/usr/bin/env bash
set -euo pipefail

# Ensure DJANGO_SETTINGS_MODULE is set; default to production settings
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-backend.production_settings}

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start Gunicorn binding to Render-provided $PORT (fallback 8000)
PORT_TO_BIND=${PORT:-8000}
exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT_TO_BIND} --workers 3
