import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

import example_package
from example_core.models import Note


@pytest.fixture
def signed_in(api_client: APIClient, db: None) -> APIClient:
    user = get_user_model().objects.create_user("ada", password="pw")
    api_client.force_authenticate(user)
    return api_client


def test_hello_is_public(api_client: APIClient) -> None:
    response = api_client.get("/api/v1/hello/Ada/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Ada!"}


def test_blank_name_is_a_problem(api_client: APIClient) -> None:
    response = api_client.get("/api/v1/hello/%20/")

    assert response.status_code == 400
    assert response["Content-Type"] == "application/problem+json"
    body = response.json()
    assert body["title"] == "Bad Request"
    assert body["status"] == 400
    assert body["errors"] == ["name must not be empty"]


@pytest.mark.django_db
def test_notes_need_a_signed_in_user(api_client: APIClient) -> None:
    response = api_client.get("/api/v1/notes/")

    assert response.status_code == 403
    assert response["Content-Type"] == "application/problem+json"


def test_notes_crud(signed_in: APIClient) -> None:
    created = signed_in.post("/api/v1/notes/", {"title": "First", "body": "Hi"}, format="json")
    assert created.status_code == 201
    note_id = created.json()["id"]

    listed = signed_in.get("/api/v1/notes/").json()
    assert listed["count"] == 1
    assert listed["results"][0]["title"] == "First"

    updated = signed_in.patch(f"/api/v1/notes/{note_id}/", {"title": "Renamed"}, format="json")
    assert updated.json()["title"] == "Renamed"

    assert signed_in.delete(f"/api/v1/notes/{note_id}/").status_code == 204
    assert Note.objects.count() == 0


def test_note_validation_is_a_problem(signed_in: APIClient) -> None:
    response = signed_in.post("/api/v1/notes/", {"title": ""}, format="json")

    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "Request validation failed."
    assert "title" in body["errors"]


def test_unknown_note_is_a_problem(signed_in: APIClient) -> None:
    response = signed_in.get("/api/v1/notes/999/")

    assert response.status_code == 404
    assert response["Content-Type"] == "application/problem+json"


def test_unknown_api_route_is_a_problem(api_client: APIClient) -> None:
    response = api_client.get("/api/v1/nope/")

    assert response.status_code == 404
    assert response["Content-Type"] == "application/problem+json"


def test_whoami_for_a_signed_in_user(signed_in: APIClient) -> None:
    response = signed_in.get("/api/v1/whoami/")

    assert response.json() == {"subject": "ada", "method": "session"}


def test_unexpected_errors_hide_details(
    api_client: APIClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(name: str) -> str:
        raise RuntimeError("secret detail")

    monkeypatch.setattr("example_api.views.greet", boom)
    api_client.raise_request_exception = False

    response = api_client.get("/api/v1/hello/Ada/")

    assert response.status_code == 500
    assert response["Content-Type"] == "application/problem+json"
    assert "secret detail" not in response.content.decode()


def test_schema_describes_the_api(api_client: APIClient) -> None:
    response = api_client.get("/api/schema/", HTTP_ACCEPT="application/vnd.oai.openapi+json")
    schema = response.json()

    assert schema["info"]["version"] == example_package.__version__
    assert "/api/v1/hello/{name}/" in schema["paths"]


def test_pagination_is_bounded(signed_in: APIClient) -> None:
    for number in range(3):
        signed_in.post("/api/v1/notes/", {"title": f"Note {number}"}, format="json")

    huge_limit = signed_in.get("/api/v1/notes/?limit=99999999999999999999999999")
    huge_offset = signed_in.get("/api/v1/notes/?offset=99999999999999999999999999")

    assert huge_limit.status_code == 200
    assert huge_limit.json()["count"] == 3
    assert huge_offset.status_code == 200
    assert huge_offset.json()["results"] == []
