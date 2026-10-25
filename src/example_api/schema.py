"""Describe the custom authentication classes in the OpenAPI document."""

from typing import Any

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.openapi import AutoSchema


class ApiKeyScheme(OpenApiAuthenticationExtension):  # type: ignore[no-untyped-call]
    target_class = "example_api.auth.ApiKeyAuthentication"
    name = "apiKey"

    def get_security_definition(self, auto_schema: AutoSchema) -> dict[str, Any]:
        return {"type": "apiKey", "in": "header", "name": "X-API-Key"}


class JWTScheme(OpenApiAuthenticationExtension):  # type: ignore[no-untyped-call]
    target_class = "example_api.auth.JWTAuthentication"
    name = "bearerAuth"

    def get_security_definition(self, auto_schema: AutoSchema) -> dict[str, Any]:
        return {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
