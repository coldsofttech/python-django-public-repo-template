"""Error responses in the RFC 9457 "problem details" format."""

from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from django.http import JsonResponse

PROBLEM_JSON = "application/problem+json"


def problem_body(status_code: int, detail: str | None = None, **extra: Any) -> dict[str, Any]:
    """Build the JSON body of a problem details response."""
    body: dict[str, Any] = {
        "type": "about:blank",
        "title": HTTPStatus(status_code).phrase,
        "status": status_code,
    }
    if detail:
        body["detail"] = detail
    body.update(extra)
    return body


def problem_response(
    status_code: int,
    detail: str | None = None,
    headers: Mapping[str, str] | None = None,
    **extra: Any,
) -> JsonResponse:
    """Build a problem details response."""
    response = JsonResponse(
        problem_body(status_code, detail, **extra),
        status=status_code,
        content_type=PROBLEM_JSON,
    )
    for name, value in (headers or {}).items():
        response[name] = value
    return response
