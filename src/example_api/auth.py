"""Authentication for the API, chosen with ``EXAMPLE_API_AUTH_MODE``.

- ``none``: every request is anonymous (local development).
- ``session``: Django's login session, with CSRF protection (default; same as the UI and admin).
- ``api_key``: callers send a shared secret in the ``X-API-Key`` header. Suited to
  service-to-service calls.
- ``jwt``: callers send ``Authorization: Bearer <token>``. Suited to tokens issued by an identity
  provider. Use an asymmetric algorithm (for example ``RS256``) and the provider's public key in
  production.
"""

import secrets
from dataclasses import dataclass

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request


@dataclass(frozen=True)
class Principal:
    """The caller of an API-key or JWT request. It stands in for a user object."""

    subject: str
    method: str
    is_authenticated: bool = True
    is_anonymous: bool = False

    @property
    def username(self) -> str:
        return self.subject


class ApiKeyAuthentication(BaseAuthentication):
    """Accept a request whose ``X-API-Key`` header matches one of ``EXAMPLE_API_KEYS``."""

    def authenticate(self, request: Request) -> tuple[Principal, None] | None:
        supplied = request.headers.get("X-API-Key")
        if supplied is None:
            return None
        if any(
            secrets.compare_digest(supplied.encode(), key.encode()) for key in settings.API_KEYS
        ):
            return Principal(subject="api-key", method="api_key"), None
        raise AuthenticationFailed("Invalid API key.")

    def authenticate_header(self, request: Request) -> str:
        return "ApiKey"


class JWTAuthentication(BaseAuthentication):
    """Accept a bearer token signed with ``EXAMPLE_JWT_KEY`` that carries ``exp`` and ``sub``."""

    def authenticate(self, request: Request) -> tuple[Principal, str] | None:
        parts = get_authorization_header(request).split()
        if not parts or parts[0].lower() != b"bearer":
            return None
        if len(parts) != 2:
            raise AuthenticationFailed("Invalid token header.")
        try:
            token = parts[1].decode()
            claims = jwt.decode(
                token,
                key=settings.JWT_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                audience=settings.JWT_AUDIENCE,
                issuer=settings.JWT_ISSUER,
                options={"require": ["exp", "sub"]},
            )
        except (UnicodeError, jwt.InvalidTokenError) as exc:
            raise AuthenticationFailed("Invalid token.") from exc
        return Principal(subject=str(claims["sub"]), method="jwt"), token

    def authenticate_header(self, request: Request) -> str:
        return "Bearer"
