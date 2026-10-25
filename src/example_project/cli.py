"""Command line entry points.

``example-manage`` is Django's ``manage.py``. ``example-serve`` starts a production server:
gunicorn for WSGI (``EXAMPLE_SERVER=wsgi``, the default) or uvicorn for ASGI (``asgi``).
"""

import os
import sys
from dataclasses import dataclass

import environ

SETTINGS_MODULE = "example_project.settings"


def manage() -> None:
    """Run a Django management command, for example ``example-manage migrate``."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


@dataclass(frozen=True)
class ServerConfig:
    """Server options, read from ``EXAMPLE_*`` environment variables."""

    server: str
    host: str
    port: int
    workers: int
    shutdown_timeout: int
    forwarded_allow_ips: str

    @classmethod
    def from_env(cls, env: environ.Env) -> "ServerConfig":
        server = env.str("EXAMPLE_SERVER", default="wsgi").lower()
        if server not in {"wsgi", "asgi"}:
            raise SystemExit(f"EXAMPLE_SERVER must be wsgi or asgi, not {server!r}.")
        return cls(
            server=server,
            host=env.str("EXAMPLE_HOST", default="127.0.0.1"),
            port=env.int("EXAMPLE_PORT", default=8000),
            workers=max(1, env.int("EXAMPLE_WORKERS", default=1)),
            shutdown_timeout=max(1, env.int("EXAMPLE_SHUTDOWN_TIMEOUT", default=10)),
            forwarded_allow_ips=env.str("EXAMPLE_FORWARDED_ALLOW_IPS", default="127.0.0.1"),
        )


def gunicorn_command(config: ServerConfig) -> list[str]:
    """The command that serves the WSGI application with gunicorn."""
    return [
        sys.executable,
        "-m",
        "gunicorn",
        "example_project.wsgi:application",
        "--bind",
        f"{config.host}:{config.port}",
        "--workers",
        str(config.workers),
        "--graceful-timeout",
        str(config.shutdown_timeout),
        "--forwarded-allow-ips",
        config.forwarded_allow_ips,
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
    ]


def serve() -> None:
    """Start the server chosen by ``EXAMPLE_SERVER`` (default ``wsgi``)."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    config = ServerConfig.from_env(environ.Env())
    if config.server == "wsgi":
        if sys.platform == "win32":
            raise SystemExit(
                "gunicorn does not run on Windows. "
                "Use EXAMPLE_SERVER=asgi, or `example-manage runserver`."
            )
        command = gunicorn_command(config)
        # Replace this process so signals (for example SIGTERM from Docker) reach gunicorn.
        os.execv(command[0], command)  # noqa: S606
    import uvicorn

    uvicorn.run(
        "example_project.asgi:application",
        host=config.host,
        port=config.port,
        workers=config.workers,
        timeout_graceful_shutdown=config.shutdown_timeout,
        proxy_headers=True,
        forwarded_allow_ips=config.forwarded_allow_ips,
        lifespan="off",  # Django does not use ASGI lifespan events
        log_config=None,  # keep logs on Django's JSON handler
    )
