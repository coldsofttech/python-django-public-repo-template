import time

import jwt
import pytest
from django.test import override_settings
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from example_api.auth import ApiKeyAuthentication, JWTAuthentication
from example_api.views import WhoAmIView

KEY = "test-signing-key-with-at-least-32-bytes"
factory = APIRequestFactory()


def _call(
    authentication: list[type[ApiKeyAuthentication | JWTAuthentication]],
    permission: type[BasePermission],
    **headers: str,
) -> Response:
    view = WhoAmIView.as_view(
        authentication_classes=authentication, permission_classes=[permission]
    )
    request = factory.get("/api/v1/whoami/")
    request.META.update(headers)
    response = view(request)
    assert isinstance(response, Response)
    return response


def _token(**claims: object) -> str:
    payload = {"sub": "ada", "exp": int(time.time()) + 60, **claims}
    return jwt.encode(payload, KEY, algorithm="HS256")


def _foreign_token() -> str:
    """A well-formed token signed with a key the server does not know."""
    claims = {"sub": "x", "exp": int(time.time()) + 60}
    return jwt.encode(claims, "a-different-key-with-32-bytes-or-more!", algorithm="HS256")


def test_none_mode_is_anonymous() -> None:
    response = _call([], AllowAny)

    assert response.data == {"subject": "anonymous", "method": "none"}


@override_settings(API_KEYS=["k1", "k2"])
def test_api_key_accepts_a_valid_key() -> None:
    response = _call([ApiKeyAuthentication], IsAuthenticated, HTTP_X_API_KEY="k2")

    assert response.status_code == 200
    assert response.data == {"subject": "api-key", "method": "api_key"}


@override_settings(API_KEYS=["k1"])
@pytest.mark.parametrize("headers", [{}, {"HTTP_X_API_KEY": "wrong"}])
def test_api_key_rejects_missing_or_wrong_keys(headers: dict[str, str]) -> None:
    response = _call([ApiKeyAuthentication], IsAuthenticated, **headers)

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == "ApiKey"


@override_settings(JWT_KEY=KEY)
def test_jwt_accepts_a_valid_token() -> None:
    response = _call([JWTAuthentication], IsAuthenticated, HTTP_AUTHORIZATION=f"Bearer {_token()}")

    assert response.status_code == 200
    assert response.data == {"subject": "ada", "method": "jwt"}


@override_settings(JWT_KEY=KEY)
@pytest.mark.parametrize(
    "authorization",
    [
        None,
        "Bearer not-a-token",
        "Bearer",
        f"Bearer {_token(exp=int(time.time()) - 60)}",
        f"Bearer {_foreign_token()}",
    ],
    ids=["missing", "garbage", "no-token", "expired", "foreign-key"],
)
def test_jwt_rejects_bad_tokens(authorization: str | None) -> None:
    headers = {"HTTP_AUTHORIZATION": authorization} if authorization else {}

    response = _call([JWTAuthentication], IsAuthenticated, **headers)

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == "Bearer"


@override_settings(JWT_KEY=KEY, JWT_AUDIENCE="my-api", JWT_ISSUER="https://issuer.example")
def test_jwt_checks_audience_and_issuer() -> None:
    good = _token(aud="my-api", iss="https://issuer.example")
    wrong_audience = _token(aud="other", iss="https://issuer.example")

    ok = _call([JWTAuthentication], IsAuthenticated, HTTP_AUTHORIZATION=f"Bearer {good}")
    bad = _call([JWTAuthentication], IsAuthenticated, HTTP_AUTHORIZATION=f"Bearer {wrong_audience}")

    assert ok.status_code == 200
    assert bad.status_code == 401
