"""Cross-cutting middleware: request IDs, security headers and rate limiting."""

import math
import time
import uuid
from collections.abc import Callable

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseBase

from example_core.logs import request_id_var
from example_core.net import client_ip
from example_core.problem import problem_response

GetResponse = Callable[[HttpRequest], HttpResponseBase]

REQUEST_ID_HEADER = "X-Request-ID"
EXEMPT_PATHS = frozenset({"/health", "/ready"})
WINDOW_SECONDS = 60

API_CSP = "default-src 'none'; frame-ancestors 'none'"
UI_CSP = "default-src 'self'; frame-ancestors 'none'; form-action 'self'"
HSTS = "max-age=31536000; includeSubDomains"


class RequestIdMiddleware:
    """Reuse the caller's ``X-Request-ID`` or create one, and return it on the response."""

    def __init__(self, get_response: GetResponse) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        try:
            response = self.get_response(request)
        finally:
            request_id_var.reset(token)
        response[REQUEST_ID_HEADER] = request_id
        return response


class SecurityHeadersMiddleware:
    """Add a Content-Security-Policy and cache rules to API and UI responses.

    The admin and the API docs load their own scripts and styles, so they get no policy here.
    Django's own security middleware adds the other headers (nosniff, referrer policy, HSTS).
    """

    def __init__(self, get_response: GetResponse) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        response = self.get_response(request)
        path = request.path_info
        api_docs = path.startswith("/api/docs") or path.startswith("/api/redoc")
        is_api = path.startswith("/api/") and not api_docs
        if is_api:
            response.headers.setdefault("Content-Security-Policy", API_CSP)
            response.headers.setdefault("Cache-Control", "no-store")
        elif not api_docs and not path.startswith(f"/{settings.ADMIN_URL}"):
            response.headers.setdefault("Content-Security-Policy", UI_CSP)
        return response


class RateLimitMiddleware:
    """Count requests per client in fixed windows and answer ``429`` over the limit.

    Counters live in Django's cache. The default per-process cache gives each instance its own
    limit. Point ``CACHE_URL`` at a shared cache such as Redis for one limit across instances.
    """

    def __init__(self, get_response: GetResponse) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        limit = settings.RATE_LIMIT_PER_MINUTE
        path = request.path_info
        if limit < 1 or path in EXEMPT_PATHS or path.startswith(settings.STATIC_URL_PATH):
            return self.get_response(request)

        now = time.time()
        window = int(now // WINDOW_SECONDS)
        reset = max(1, math.ceil((window + 1) * WINDOW_SECONDS - now))
        key = f"ratelimit:{client_ip(request, settings.PROXY_COUNT)}:{window}"
        cache.add(key, 0, timeout=WINDOW_SECONDS + 1)
        count = cache.incr(key)
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(max(0, limit - count)),
            "X-RateLimit-Reset": str(reset),
        }
        if count > limit:
            headers["Retry-After"] = str(reset)
            return self._too_many(request, headers)

        response = self.get_response(request)
        for name, value in headers.items():
            response[name] = value
        return response

    @staticmethod
    def _too_many(request: HttpRequest, headers: dict[str, str]) -> HttpResponseBase:
        if request.path_info.startswith("/api/"):
            return problem_response(429, "Too many requests. Try again later.", headers=headers)
        response = HttpResponse("Too many requests. Try again later.", status=429)
        for name, value in headers.items():
            response[name] = value
        return response
