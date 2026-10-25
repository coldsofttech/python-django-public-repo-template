import pytest
from django.test import Client, override_settings


@pytest.mark.django_db
@pytest.mark.parametrize("path", ["/health", "/ready"])
@override_settings(ROOT_URLCONF="tests.urlconfs.all_off")
def test_probes_exist_even_when_every_feature_is_off(client: Client, path: str) -> None:
    assert client.get(path).status_code == 200


@pytest.mark.parametrize(
    "path", ["/api/v1/hello/Ada/", "/api/schema/", "/", "/accounts/login/", "/admin/"]
)
@override_settings(ROOT_URLCONF="tests.urlconfs.all_off")
def test_disabled_features_have_no_routes(client: Client, path: str) -> None:
    assert client.get(path).status_code == 404


@override_settings(ROOT_URLCONF="tests.urlconfs.api_only")
def test_api_without_ui(client: Client) -> None:
    assert client.get("/api/v1/hello/Ada/").status_code == 200
    assert client.get("/api/schema/").status_code == 200
    assert client.get("/").status_code == 404


@override_settings(ROOT_URLCONF="tests.urlconfs.api_without_docs")
def test_docs_can_be_hidden_separately(client: Client) -> None:
    assert client.get("/api/v1/hello/Ada/").status_code == 200
    assert client.get("/api/schema/").status_code == 404
    assert client.get("/api/docs/").status_code == 404


@override_settings(ROOT_URLCONF="tests.urlconfs.ui_only")
def test_ui_without_api(client: Client) -> None:
    assert client.get("/").status_code == 200
    assert client.get("/api/v1/hello/Ada/").status_code == 404


@override_settings(ROOT_URLCONF="tests.urlconfs.custom_admin")
def test_admin_url_can_be_moved(client: Client) -> None:
    assert client.get("/admin/").status_code == 404
    assert client.get("/manage-site/", follow=False).status_code == 302
