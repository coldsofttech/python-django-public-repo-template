"""Health probes and error pages."""

import logging

from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.defaults import page_not_found, server_error

from example_core.problem import problem_response
from example_package import __version__

logger = logging.getLogger(__name__)


def health(request: HttpRequest) -> JsonResponse:
    """Liveness probe: 200 while the process runs. It never touches the database."""
    return JsonResponse({"status": "ok"})


def ready(request: HttpRequest) -> JsonResponse:
    """Readiness probe: 200 when the database answers, 503 when it does not."""
    try:
        connection.ensure_connection()
    except Exception:
        logger.exception("Readiness check failed")
        return problem_response(503, "The database is not reachable.")
    return JsonResponse({"status": "ready", "version": __version__})


def not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """404 page, as problem details for API paths."""
    if request.path_info.startswith("/api/"):
        return problem_response(404)
    return page_not_found(request, exception)


def error(request: HttpRequest) -> HttpResponse:
    """500 page, as problem details for API paths. Details are never exposed."""
    if request.path_info.startswith("/api/"):
        return problem_response(500)
    return server_error(request)
