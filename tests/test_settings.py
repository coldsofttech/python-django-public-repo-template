import os
import subprocess
import sys

import pytest

PRODUCTION = {
    "EXAMPLE_SECRET_KEY": "test-only-not-a-real-secret-" * 3,
    "EXAMPLE_ALLOWED_HOSTS": "example.com",
    "EXAMPLE_BEHIND_PROXY": "true",
}


def _run(args: list[str], **env: str) -> subprocess.CompletedProcess[str]:
    base = {k: v for k, v in os.environ.items() if not k.startswith(("EXAMPLE_", "DATABASE_URL"))}
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        check=False,
        env={**base, "DJANGO_SETTINGS_MODULE": "example_project.settings", **env},
    )


def _import_settings(**env: str) -> subprocess.CompletedProcess[str]:
    return _run(["-c", "import example_project.settings"], **env)


def test_deployment_check_passes_for_a_production_configuration() -> None:
    result = _run(
        ["-m", "example_project", "check", "--deploy", "--fail-level", "WARNING"], **PRODUCTION
    )

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("env", "message"),
    [
        ({"EXAMPLE_ALLOWED_HOSTS": "example.com"}, "EXAMPLE_SECRET_KEY is required"),
        ({"EXAMPLE_SECRET_KEY": "x"}, "EXAMPLE_ALLOWED_HOSTS is required"),
        ({**PRODUCTION, "EXAMPLE_API_AUTH_MODE": "magic"}, "EXAMPLE_API_AUTH_MODE must be one of"),
        ({**PRODUCTION, "EXAMPLE_API_AUTH_MODE": "api_key"}, "EXAMPLE_API_KEYS is required"),
        ({**PRODUCTION, "EXAMPLE_API_AUTH_MODE": "jwt"}, "EXAMPLE_JWT_KEY is required"),
    ],
)
def test_misconfiguration_stops_startup(env: dict[str, str], message: str) -> None:
    result = _import_settings(**env)

    assert result.returncode != 0
    assert message in result.stderr


def test_development_mode_needs_no_configuration() -> None:
    assert _import_settings(EXAMPLE_DEBUG="true").returncode == 0


def test_database_url_selects_the_database() -> None:
    result = _run(
        ["-c", "from django.conf import settings; print(settings.DATABASES['default']['ENGINE'])"],
        EXAMPLE_DEBUG="true",
        DATABASE_URL="postgres://user:pw@db.example:5432/app",
    )

    assert result.stdout.strip() == "django.db.backends.postgresql"
