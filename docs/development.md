# Development

## Layout

```text
src/example_package/   library: all the logic, no web code (typed)
src/example_project/   Django project: settings, URLs, WSGI/ASGI entry points, example-manage and example-serve
src/example_core/      Django app: models, admin, health probes, request ID, rate limit and security middleware
src/example_api/       optional REST API (Django REST Framework)
src/example_web/       optional server-rendered UI (templates and HTMX)
tests/                 unit tests with pytest-django
tests/integration/     tests that start the real server (WSGI and ASGI) and fuzz the API
pyproject.toml         metadata, dependencies, optional database drivers and tool configuration
uv.lock                locked dependencies (commit this file)
docs/openapi.json      the API contract, generated from the code
```

The example names are `example_package` (library), `example_project`, `example_core`, `example_api` and `example_web` (Django packages), the `example-manage` and `example-serve` commands, the `EXAMPLE_` settings prefix and `example-django` (the Docker image tag used in CI). After creating a repo from this template:

1. Rename the five packages under `src/` to your import names, and update the imports in `src/`, `tests/` and `scripts/`.
2. In `pyproject.toml`, update `[tool.hatch.version]`, `[tool.hatch.build.targets.wheel]`, the `[project.scripts]` entries, the `--cov=` options, and `django_settings_module`.
3. Update the app names in `INSTALLED_APPS`, `MIDDLEWARE` and the `REST_FRAMEWORK` paths in `settings.py`, plus `apps.py` in each app.
4. Replace the `EXAMPLE_` prefix in `settings.py`, `cli.py`, `.env.example`, `Dockerfile`, `compose.yaml`, the workflows and the docs.
5. Delete what you do not need: `example_api` and its tests if you have no API, `example_web` if you have no UI. Then remove them from `INSTALLED_APPS` and `urls.py`.
6. Replace the example `Note` model with yours, delete `src/example_core/migrations/0001_initial.py`, and run `uv run example-manage makemigrations`.
7. Set the description in `pyproject.toml`, run `uv lock`, and regenerate the contract with `uv run python scripts/export_openapi.py`.

## Tooling

| Purpose | Tool |
| --- | --- |
| Environment, dependencies, build | [uv](https://docs.astral.sh/uv/) with Hatchling |
| Framework | Django, Django REST Framework, drf-spectacular (OpenAPI) |
| Lint and format | Ruff, including its Django and security rules |
| Type checking | mypy (strict) with django-stubs |
| Tests and coverage | pytest with pytest-django and pytest-cov (80% minimum) |
| Static files | WhiteNoise |
| Servers | gunicorn (WSGI), uvicorn (ASGI) |

```bash
uv sync                                  # create .venv and install dev dependencies (SQLite)
uv sync --extra postgres                 # ...with the PostgreSQL driver (or --extra mysql)
cp .env.example .env                     # then set EXAMPLE_DEBUG=true for local work
uv run example-manage migrate            # create the database
uv run example-manage createsuperuser    # an admin and UI account
uv run example-manage runserver          # development server with auto-reload
uv run pytest                            # unit tests with coverage
uv run pytest -m integration --no-cov    # integration tests only
uv run ruff check . && uv run ruff format .
uv run mypy
uv run example-manage check --deploy     # review production settings
uv run python scripts/export_openapi.py  # regenerate docs/openapi.json
docker compose up --build                # run in containers with PostgreSQL
```

On Windows keep the project in a short path: some packages (for example the API docs assets) have long file names that break under the 260-character path limit.

## Integration tests

Tests under `tests/integration/` are marked `integration` automatically by that folder's `conftest.py`. They are excluded from the default `pytest` run, and therefore from the pre-commit hook, and run as their own job in CI. They migrate a temporary SQLite database, collect static files, start the real server through `example-serve` on both **gunicorn (WSGI)** and **uvicorn (ASGI)**, and then call it over HTTP. One test runs Schemathesis, which generates requests from the OpenAPI document and fails on any server error. The WSGI cases are skipped on Windows, where gunicorn does not run.

## Continuous integration

The `ci` workflow runs these jobs, and a final `ci` job gates on all of them and is the single required check in the branch ruleset:

- `lint`: pre-commit (Ruff, mypy and more), no missing migrations, `check --deploy` with a production-like configuration, and a check that `docs/openapi.json` is up to date.
- `test`: unit tests on Python 3.11 to 3.15 on Ubuntu, and 3.11 on Windows and macOS.
- `postgres` and `mysql`: the same test suite against real database servers.
- `integration`: the real-server tests above, on the same matrix as `test`.
- `docker`: builds the image for PostgreSQL, MySQL and SQLite, checks the driver imports, then migrates and probes `/ready` in a running container.
- `build`: builds the package, runs `twine check`, and confirms templates, static files and migrations are in the wheel.

Django 5.2 (LTS) and 6.0 support different Python versions, so the lock file picks the right Django for each Python in the matrix.

## Releasing

Releases are triggered by publishing a GitHub release tagged `v<version>`. Publishing is off by default. Turn on the targets you want with repository variables (the settings script creates both set to `false`):

```bash
gh variable set PUBLISH_GHCR --body true   # Docker image to ghcr.io/<owner>/<repo>
gh variable set PUBLISH_PYPI --body true   # package to PyPI
gh variable set DOCKER_UV_EXTRAS --body "--extra mysql"   # optional: database drivers in the image
```

1. Bump `__version__` in `src/<package>/__init__.py` and update `CHANGELOG.md`.
2. Publish a GitHub release tagged `v<version>`. The workflow fails if the tag and version differ.

**GHCR:** the image is tagged with the version, `major.minor` and `latest`, and a build provenance attestation is attached. It includes the PostgreSQL driver unless you set `DOCKER_UV_EXTRAS`. Make the package public in its settings if you want anyone to pull it.

**PyPI** uses [trusted publishing](https://docs.pypi.org/trusted-publishers/), so no API token is stored. Before the first release, add a trusted publisher on PyPI for this repository: workflow `release.yml`, environment `pypi`. The settings script creates the `pypi` environment and restricts it to `v*` tags. Publishing a Django project to PyPI only makes sense if it is meant to be installed as a reusable package.
