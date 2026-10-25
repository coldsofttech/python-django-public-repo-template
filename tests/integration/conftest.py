import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark every test in this directory as an integration test."""
    for item in items:
        if "integration" in item.path.parts:
            item.add_marker(pytest.mark.integration)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def scripts_dir() -> Path:
    return Path(sys.executable).parent


@pytest.fixture(scope="session", params=["wsgi", "asgi"])
def base_url(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> Iterator[str]:
    """Run the real server in a subprocess, the way users start it, on each server type."""
    server: str = request.param
    if server == "wsgi" and sys.platform == "win32":
        pytest.skip("gunicorn does not run on Windows")

    data = tmp_path_factory.mktemp(f"data-{server}")
    port = _free_port()
    env = {
        **{k: v for k, v in os.environ.items() if not k.startswith(("EXAMPLE_", "DATABASE_URL"))},
        # pytest-django points this at the test settings; the server must use the real ones.
        "DJANGO_SETTINGS_MODULE": "example_project.settings",
        "EXAMPLE_SECRET_KEY": "integration-test-secret-key-" + "x" * 40,
        "EXAMPLE_ALLOWED_HOSTS": "127.0.0.1",
        "EXAMPLE_HTTPS": "false",
        "EXAMPLE_SERVER": server,
        "EXAMPLE_HOST": "127.0.0.1",
        "EXAMPLE_PORT": str(port),
        "EXAMPLE_DATA_DIR": str(data),
        "EXAMPLE_STATIC_ROOT": str(data / "static"),
        # The contract test sends many requests from one address and needs open endpoints.
        "EXAMPLE_RATE_LIMIT_PER_MINUTE": "0",
        "EXAMPLE_API_AUTH_MODE": "none",
        "PYTHONIOENCODING": "utf-8",
    }
    manage = [sys.executable, "-m", "example_project"]
    subprocess.run([*manage, "migrate", "--noinput"], env=env, check=True, capture_output=True)
    subprocess.run(
        [*manage, "collectstatic", "--noinput"], env=env, check=True, capture_output=True
    )

    process = subprocess.Popen(
        [sys.executable, "-c", "from example_project.cli import serve; serve()"], env=env
    )
    url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            if process.poll() is not None:
                pytest.fail("server exited during startup")
            try:
                if httpx.get(f"{url}/health", timeout=1).status_code == 200:
                    break
            except httpx.TransportError:
                time.sleep(0.2)
        else:
            pytest.fail("server did not become ready")
        yield url
    finally:
        process.terminate()
        process.wait(timeout=15)
