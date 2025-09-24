"""Temporary test runner shim to provide minimal fake modules so Django settings can import
without installing heavy dependencies in the environment. This is for local CI-style test runs only.
"""
import sys
import types
import os
import types as _types

# Mark that we're running tests so settings.py can switch to sqlite for local test runs
os.environ.setdefault('DJANGO_TESTING', '1')

# Provide a minimal 'decouple' module with 'config' and 'Csv' to satisfy settings import
decouple_mod = _types.ModuleType('decouple')

def config(name, default=None, cast=None):
    # Look up environment variables first
    val = os.environ.get(name)
    if val is None:
        val = default
    if cast and val is not None:
        try:
            return cast(val)
        except Exception:
            # fallback to default if casting fails
            return default
    return val

decouple_mod.config = config

class Csv(list):
    pass

decouple_mod.Csv = Csv
sys.modules['decouple'] = decouple_mod

# Provide a dummy celery module with a minimal Celery class
celery_mod = _types.ModuleType('celery')

class DummyApp:
    def config_from_object(self, *args, **kwargs):
        return None

    def autodiscover_tasks(self, *args, **kwargs):
        return None

    def task(self, *args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

class DummyCelery:
    def __init__(self, *args, **kwargs):
        self._app = DummyApp()

    def __call__(self, *args, **kwargs):
        return self._app

    def __getattr__(self, item):
        return getattr(self._app, item)

celery_mod.Celery = DummyCelery
sys.modules['celery'] = celery_mod

# Now run Django's test management command
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    from django.core.management import execute_from_command_line

    execute_from_command_line(['manage.py', 'test', '-v', '2'])
