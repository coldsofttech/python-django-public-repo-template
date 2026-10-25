# python-django-public-repo-template

[![CI](https://github.com/coldsofttech/python-django-public-repo-template/actions/workflows/ci.yml/badge.svg)](https://github.com/coldsofttech/python-django-public-repo-template/actions/workflows/ci.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/python-django-public-repo-template)](https://pypi.org/project/python-django-public-repo-template/)
[![Django](https://img.shields.io/badge/web-Django-092E20)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/API-Django%20REST%20Framework-A30000)](https://www.django-rest-framework.org/)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-6BA539)](docs/openapi.json)
[![Docker](https://img.shields.io/badge/container-Docker-2496ED)](Dockerfile)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/github/license/coldsofttech/python-django-public-repo-template)](LICENSE)

A ready-to-use starting point for public Django web applications on GitHub. It has a typed, tested project layout, an optional REST API and an optional built-in web UI, runs on SQLite, PostgreSQL, MySQL and other databases, serves under WSGI or ASGI, ships as a small Docker image, and includes the community and security files a public repository needs.

## What you get

- **Optional REST API** with Django REST Framework, an OpenAPI contract that CI keeps in sync, and API key, JWT or session authentication
- **Optional web UI** rendered by Django with HTMX, or leave the UI to a separate frontend repository
- **Your choice of database:** SQLite, PostgreSQL, MySQL and any other database Django supports, selected with one `DATABASE_URL`
- **WSGI (gunicorn) or ASGI (uvicorn)** with one setting
- Safe production defaults: HTTPS settings, rate limiting, security headers, a request size limit, and a deployment check that CI enforces
- Health and readiness probes, JSON logs with a request ID, and consistent error responses
- A small non-root Docker image and a Compose file with PostgreSQL
- Optional publishing of the image to GHCR and of the package to PyPI, both off until you turn them on
- Fast, reproducible setup with [uv](https://docs.astral.sh/uv/), plus linting, formatting and type checking before every commit and in CI
- Tests on Python 3.11 to 3.15 and on real PostgreSQL and MySQL servers, with Security-tab scanning (CodeQL, Semgrep, Hadolint, Trivy)
- Contribution, conduct, support and security-reporting guidelines, issue forms and automated dependency updates

## Getting started

1. Click **Use this template** on GitHub and create your new repository.
2. Run the **Init** workflow from the Actions tab and merge the pull request it opens. This fills in your owner and repository name.
3. Rename the example packages and settings prefix, and choose which optional features to keep. See the [development guide](docs/development.md).
4. Add your contact details in `CODE_OF_CONDUCT.md`, delete `.github/workflows/init.yml`, and replace this description.
5. Apply the repository protections by following the [setup guide](docs/repo-setup.md).
6. Install dependencies and commit checks:

   ```bash
   uv sync
   uv run pre-commit install --hook-type pre-commit --hook-type post-commit
   ```

## Running it

```bash
cp .env.example .env              # then add EXAMPLE_DEBUG=true for local work
uv run example-manage migrate
uv run example-manage createsuperuser
uv run example-manage runserver
```

Then open <http://127.0.0.1:8000/> for the web UI, <http://127.0.0.1:8000/api/docs/> for the interactive API docs, and <http://127.0.0.1:8000/admin/> for the admin.

With Docker and PostgreSQL:

```bash
docker compose up --build
```

For production, run `uv run example-serve` (gunicorn by default, uvicorn with `EXAMPLE_SERVER=asgi`) behind a reverse proxy that handles your domain and HTTPS. Everything is configured with environment variables.

## Documentation

- [Configuration](docs/configuration.md): every setting
- [Databases](docs/database.md): SQLite, PostgreSQL, MySQL and others
- [REST API](docs/api.md): endpoints, authentication and errors
- [User interface](docs/frontend.md): the built-in pages, or a separate frontend repository
- [Deployment](docs/deployment.md): WSGI or ASGI, domain, proxy, Docker and probes
- [Security](docs/security.md): protections and automated scanning
- [Development](docs/development.md) and [Architecture](docs/architecture.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please report security issues privately as described in [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE).
