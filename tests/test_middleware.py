import pytest
from django.test import Client, RequestFactory, override_settings

from example_core.net import client_ip


def test_request_id_is_generated(client: Client) -> None:
    assert len(client.get("/health")["X-Request-ID"]) == 32


def test_request_id_is_reused(client: Client) -> None:
    response = client.get("/health", headers={"X-Request-ID": "abc-123"})

    assert response["X-Request-ID"] == "abc-123"


def test_api_responses_get_a_strict_policy(client: Client) -> None:
    response = client.get("/api/v1/hello/Ada/")

    assert response["Content-Security-Policy"] == "default-src 'none'; frame-ancestors 'none'"
    assert response["Cache-Control"] == "no-store"
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"
    assert response["Referrer-Policy"] == "no-referrer"


def test_ui_pages_get_a_same_origin_policy(client: Client) -> None:
    response = client.get("/")

    assert response["Content-Security-Policy"].startswith("default-src 'self'")


@pytest.mark.parametrize("path", ["/api/docs/", "/api/redoc/", "/admin/login/"])
def test_docs_and_admin_pages_get_no_policy(client: Client, path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert "Content-Security-Policy" not in response


@override_settings(RATE_LIMIT_PER_MINUTE=2)
def test_rate_limit_answers_429(client: Client) -> None:
    first = client.get("/api/v1/hello/Ada/")
    client.get("/api/v1/hello/Ada/")
    third = client.get("/api/v1/hello/Ada/")

    assert first["X-RateLimit-Limit"] == "2"
    assert first["X-RateLimit-Remaining"] == "1"
    assert third.status_code == 429
    assert third["Content-Type"] == "application/problem+json"
    assert int(third["Retry-After"]) >= 1
    assert third["X-Request-ID"]


@override_settings(RATE_LIMIT_PER_MINUTE=1)
def test_rate_limit_on_pages_is_plain(client: Client) -> None:
    client.get("/")

    response = client.get("/")

    assert response.status_code == 429
    assert response["Retry-After"]


@override_settings(RATE_LIMIT_PER_MINUTE=1)
def test_probes_are_never_limited(client: Client) -> None:
    assert all(client.get("/health").status_code == 200 for _ in range(3))


@override_settings(RATE_LIMIT_PER_MINUTE=0)
def test_rate_limit_can_be_turned_off(client: Client) -> None:
    assert all(client.get("/api/v1/hello/Ada/").status_code == 200 for _ in range(10))
    assert "X-RateLimit-Limit" not in client.get("/api/v1/hello/Ada/")


@override_settings(RATE_LIMIT_PER_MINUTE=1, PROXY_COUNT=1)
def test_limits_follow_the_forwarded_client(client: Client) -> None:
    def hit(address: str) -> int:
        return client.get("/api/v1/hello/Ada/", headers={"X-Forwarded-For": address}).status_code

    assert hit("203.0.113.1") == 200
    assert hit("203.0.113.1") == 429
    assert hit("203.0.113.2") == 200


def test_client_ip_ignores_forwarded_headers_without_a_trusted_proxy() -> None:
    request = RequestFactory().get("/", REMOTE_ADDR="10.0.0.9", HTTP_X_FORWARDED_FOR="1.2.3.4")

    assert client_ip(request, proxy_count=0) == "10.0.0.9"


def test_client_ip_uses_the_entry_added_by_the_trusted_proxy() -> None:
    request = RequestFactory().get(
        "/", REMOTE_ADDR="10.0.0.9", HTTP_X_FORWARDED_FOR="6.6.6.6, 198.51.100.7"
    )

    assert client_ip(request, proxy_count=1) == "198.51.100.7"
    assert client_ip(request, proxy_count=2) == "6.6.6.6"
    assert client_ip(request, proxy_count=3) == "10.0.0.9"
