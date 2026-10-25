"""WSGI entry point, for servers such as gunicorn: ``example_project.wsgi:application``."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")

application = get_wsgi_application()
