import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from example_core.models import Note


@pytest.fixture
def signed_in(client: Client, db: None) -> Client:
    get_user_model().objects.create_user("ada", password="pw")
    client.login(username="ada", password="pw")
    return client


def test_landing_page_asks_to_sign_in(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert b"Sign in" in response.content


@pytest.mark.django_db
def test_login_page_and_sign_in(client: Client) -> None:
    get_user_model().objects.create_user("ada", password="pw")

    assert client.get("/accounts/login/").status_code == 200
    response = client.post("/accounts/login/", {"username": "ada", "password": "pw"})

    assert response.status_code == 302
    assert response["Location"] == "/"


def test_signed_in_users_see_notes(signed_in: Client) -> None:
    Note.objects.create(title="Buy milk")

    assert b"Buy milk" in signed_in.get("/").content


def test_creating_a_note_with_htmx_returns_a_fragment(signed_in: Client) -> None:
    response = signed_in.post(
        "/notes/", {"title": "Hello", "body": ""}, headers={"HX-Request": "true"}
    )

    assert response.status_code == 201
    assert b"Hello" in response.content
    assert b'hx-swap-oob="true"' in response.content
    assert Note.objects.filter(title="Hello").exists()


def test_creating_a_note_without_htmx_redirects(signed_in: Client) -> None:
    response = signed_in.post("/notes/", {"title": "Plain", "body": ""})

    assert response.status_code == 302
    assert Note.objects.filter(title="Plain").exists()


def test_invalid_note_shows_errors(signed_in: Client) -> None:
    response = signed_in.post("/notes/", {"title": "", "body": ""}, headers={"HX-Request": "true"})

    assert response.status_code == 422
    assert b"errorlist" in response.content
    assert Note.objects.count() == 0


def test_deleting_a_note(signed_in: Client) -> None:
    note = Note.objects.create(title="Temp")

    response = signed_in.post(f"/notes/{note.pk}/delete/", headers={"HX-Request": "true"})

    assert response.status_code == 200
    assert Note.objects.count() == 0


@pytest.mark.django_db
def test_anonymous_users_cannot_change_notes(client: Client) -> None:
    note = Note.objects.create(title="Keep")

    assert client.post("/notes/", {"title": "x"}).status_code == 302
    assert client.post(f"/notes/{note.pk}/delete/").status_code == 302
    assert Note.objects.count() == 1


def test_get_is_not_allowed_on_mutating_routes(signed_in: Client) -> None:
    assert signed_in.get("/notes/").status_code == 405


def test_str_of_a_note() -> None:
    assert str(Note(title="T")) == "T"
