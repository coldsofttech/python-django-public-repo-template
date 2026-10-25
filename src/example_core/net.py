"""Finding the real client address."""

from django.http import HttpRequest


def client_ip(request: HttpRequest, proxy_count: int) -> str:
    """Return the address of the caller.

    With ``proxy_count`` trusted proxies in front of the app, each one appends the address it saw
    to ``X-Forwarded-For``, so the caller is the entry ``proxy_count`` places from the end. Entries
    before that are supplied by the client and cannot be trusted. With no trusted proxy, only
    ``REMOTE_ADDR`` is used, so a client cannot spoof its address.
    """
    remote = str(request.META.get("REMOTE_ADDR") or "unknown")
    if proxy_count < 1:
        return remote
    forwarded = [
        part.strip() for part in str(request.META.get("HTTP_X_FORWARDED_FOR", "")).split(",")
    ]
    forwarded = [part for part in forwarded if part]
    if len(forwarded) < proxy_count:
        return remote
    return forwarded[-proxy_count]
