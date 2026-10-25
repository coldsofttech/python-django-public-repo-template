import subprocess
import sys

import example_package


def test_package_imports_in_fresh_interpreter() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import example_package; print(example_package.__version__)"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.strip() == example_package.__version__
