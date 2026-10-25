import os
import sys

import environ
import pytest

from example_project import cli
from example_project.cli import ServerConfig, gunicorn_command


def _env(values: dict[str, str]) -> environ.Env:
    env = environ.Env()
    env.ENVIRON = values
    return env


def test_defaults() -> None:
    config = ServerConfig.from_env(_env({}))

    assert config == ServerConfig("wsgi", "127.0.0.1", 8000, 1, 10, "127.0.0.1")


def test_environment_overrides() -> None:
    config = ServerConfig.from_env(
        _env(
            {
                "EXAMPLE_SERVER": "ASGI",
                "EXAMPLE_HOST": "10.1.2.3",
                "EXAMPLE_PORT": "9000",
                "EXAMPLE_WORKERS": "4",
                "EXAMPLE_SHUTDOWN_TIMEOUT": "30",
                "EXAMPLE_FORWARDED_ALLOW_IPS": "10.0.0.0/8",
            }
        )
    )

    assert config.server == "asgi"
    assert config.host == "10.1.2.3"
    assert (config.port, config.workers, config.shutdown_timeout) == (9000, 4, 30)
    assert config.forwarded_allow_ips == "10.0.0.0/8"


def test_unknown_server_is_rejected() -> None:
    with pytest.raises(SystemExit, match="wsgi or asgi"):
        ServerConfig.from_env(_env({"EXAMPLE_SERVER": "cgi"}))


def test_gunicorn_command() -> None:
    command = gunicorn_command(ServerConfig("wsgi", "10.1.2.3", 8080, 3, 20, "*"))

    assert command[:4] == [sys.executable, "-m", "gunicorn", "example_project.wsgi:application"]
    assert command[command.index("--bind") + 1] == "10.1.2.3:8080"
    assert command[command.index("--workers") + 1] == "3"
    assert command[command.index("--forwarded-allow-ips") + 1] == "*"


@pytest.mark.skipif(sys.platform == "win32", reason="gunicorn does not run on Windows")
def test_serve_replaces_the_process_with_gunicorn(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(os, "execv", lambda path, args: calls.append(args))
    monkeypatch.delenv("EXAMPLE_SERVER", raising=False)

    cli.serve()

    assert calls[0][3] == "example_project.wsgi:application"


def test_serve_asgi_runs_uvicorn(monkeypatch: pytest.MonkeyPatch) -> None:
    import uvicorn

    calls: list[tuple[str, dict[str, object]]] = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **kwargs: calls.append((app, kwargs)))
    monkeypatch.setenv("EXAMPLE_SERVER", "asgi")
    monkeypatch.setenv("EXAMPLE_PORT", "9001")

    cli.serve()

    app, kwargs = calls[0]
    assert app == "example_project.asgi:application"
    assert kwargs["port"] == 9001
    assert kwargs["proxy_headers"] is True
    assert kwargs["lifespan"] == "off"


def test_wsgi_on_windows_explains_the_alternative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.delenv("EXAMPLE_SERVER", raising=False)

    with pytest.raises(SystemExit, match="EXAMPLE_SERVER=asgi"):
        cli.serve()


def test_manage_runs_a_django_command(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["example-manage", "--version"])

    cli.manage()

    assert capsys.readouterr().out.strip()
