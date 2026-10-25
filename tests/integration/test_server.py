import httpx

import example_package


def test_health(base_url: str) -> None:
    assert httpx.get(f"{base_url}/health").json() == {"status": "ok"}


def test_ready_checks_the_database(base_url: str) -> None:
    assert httpx.get(f"{base_url}/ready").json()["version"] == example_package.__version__


def test_api_hello(base_url: str) -> None:
    assert httpx.get(f"{base_url}/api/v1/hello/Ada/").json() == {"message": "Hello, Ada!"}


def test_api_notes_round_trip(base_url: str) -> None:
    created = httpx.post(f"{base_url}/api/v1/notes/", json={"title": "From a test"})
    assert created.status_code == 201

    listed = httpx.get(f"{base_url}/api/v1/notes/").json()

    assert "From a test" in [note["title"] for note in listed["results"]]


def test_ui_page_and_security_headers(base_url: str) -> None:
    response = httpx.get(f"{base_url}/")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["content-security-policy"].startswith("default-src 'self'")
    assert response.headers["x-request-id"]


def test_static_files_are_served_by_the_app(base_url: str) -> None:
    response = httpx.get(f"{base_url}/static/example_web/htmx.min.js")

    assert response.status_code == 200
    assert "htmx" in response.text


def test_api_docs_are_served(base_url: str) -> None:
    assert httpx.get(f"{base_url}/api/docs/").status_code == 200
    assert httpx.get(f"{base_url}/api/schema/").status_code == 200


def test_admin_login_page(base_url: str) -> None:
    assert httpx.get(f"{base_url}/admin/login/").status_code == 200
