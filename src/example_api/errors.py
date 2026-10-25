"""Turn API errors into RFC 9457 problem details."""

from typing import Any

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from example_core.problem import PROBLEM_JSON, problem_body


def problem_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Use DRF's handling, but answer with ``application/problem+json``.

    Unexpected errors are not handled here: they reach Django's 500 handler, which never exposes
    details.
    """
    response = exception_handler(exc, context)
    if response is None:
        return None
    if isinstance(exc, ValidationError):
        body = problem_body(
            response.status_code, "Request validation failed.", errors=response.data
        )
    else:
        detail = response.data.get("detail") if isinstance(response.data, dict) else None
        body = problem_body(response.status_code, str(detail) if detail else None)
    response.data = body
    response.content_type = PROBLEM_JSON
    return response
