"""ASGI entry point, for servers such as uvicorn: ``example_project.asgi:application``."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")

application = get_asgi_application()
