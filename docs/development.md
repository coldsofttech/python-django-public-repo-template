# Development

## Layout

```text
src/example_package/   package source (src layout, typed)
tests/                 pytest tests
pyproject.toml         metadata, dependencies and tool configuration
uv.lock                locked dependencies (commit this file)
```

The package is named `example_package`. After creating a repo from this template:

1. Rename `src/example_package/` to your import name.
2. Update `[tool.hatch.version]`, `[tool.hatch.build.targets.wheel]` and `--cov=` in `pyproject.toml`, and the import in `tests/`.
3. Set the description in `pyproject.toml`, then run `uv lock`.

## Tooling

| Purpose | Tool |
| --- | --- |
| Environment, dependencies, build | [uv](https://docs.astral.sh/uv/) with Hatchling |
| Lint and format | Ruff |
| Type checking | mypy (strict) |
| Tests and coverage | pytest with pytest-cov (80% minimum) |

```bash
uv sync                    # create .venv and install dev dependencies
uv run pytest              # unit tests with coverage (skips integration tests)
uv run pytest -m integration --no-cov   # integration tests only
uv run ruff check .        # lint
uv run ruff format .       # format
uv run mypy                # type check
uv build                   # build sdist and wheel
```

## Integration tests

Tests under `tests/integration/` are marked `integration` automatically by that folder's `conftest.py`. They are excluded from the default `pytest` run, and therefore from the pre-commit hook, and run as their own job in CI. Put slower or end-to-end tests there.

## Continuous integration

The `ci` workflow runs four jobs: `lint` (pre-commit, including Ruff and mypy), `test` (unit tests), `integration` (tests marked `integration`) and `build` (build and `twine check`). The `test` and `integration` jobs run on Python 3.11 to 3.15 on Ubuntu, and on 3.11 on Windows and macOS. A final `ci` job gates on all four and is the single required check in the branch ruleset.

## Releasing to PyPI

Publishing uses [trusted publishing](https://docs.pypi.org/trusted-publishers/), so no API token is stored.

1. On PyPI, add a trusted publisher for this repository: workflow `release.yml`, environment `pypi`.
2. Create an environment named `pypi`. The settings script does this and restricts it to `v*` tags.
3. Bump `__version__` in `src/<package>/__init__.py` and update `CHANGELOG.md`.
4. Publish a GitHub release tagged `v<version>`. The workflow fails if the tag and version differ.
