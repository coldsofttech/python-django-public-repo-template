import os
import subprocess
import sys

from tests.integration.conftest import scripts_dir


def test_documented_requests_never_cause_server_errors(base_url: str) -> None:
    """Schemathesis generates requests from the OpenAPI document and checks for 5xx responses."""
    name = "schemathesis.exe" if sys.platform == "win32" else "schemathesis"
    command = [
        str(scripts_dir() / name),
        "run",
        f"{base_url}/api/schema/",
        "--checks",
        "not_a_server_error",
        "--max-examples",
        "25",
        "--no-color",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )

    assert result.returncode == 0, result.stdout + result.stderr
