import pytest
from django.db import connection
from django.test import Client

import example_package


def test_health(client: Client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_ready_reports_version(client: Client) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "version": example_package.__version__}


@pytest.mark.django_db
def test_ready_is_503_when_the_database_is_down(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken() -> None:
        raise RuntimeError("database is down")

    monkeypatch.setattr(connection, "ensure_connection", broken)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response["Content-Type"] == "application/problem+json"
    assert "database is down" not in response.content.decode()
