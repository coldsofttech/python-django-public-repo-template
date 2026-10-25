# syntax=docker/dockerfile:1

FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

# Database drivers to include: "--extra postgres" (default), "--extra mysql", both, or empty for
# SQLite only. Build with, for example: docker build --build-arg UV_EXTRAS="--extra mysql" .
ARG UV_EXTRAS="--extra postgres"

# The MySQL driver is compiled, so it needs build tools and the client library headers.
# hadolint ignore=DL3008
RUN case "$UV_EXTRAS" in \
      *mysql*) apt-get update \
        && apt-get install -y --no-install-recommends build-essential pkg-config default-libmysqlclient-dev \
        && rm -rf /var/lib/apt/lists/* ;; \
    esac

# Dependencies first, so this layer is cached until the lockfile changes.
COPY pyproject.toml uv.lock README.md LICENSE ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project $UV_EXTRAS

COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable $UV_EXTRAS

FROM python:3.13-slim
ARG UV_EXTRAS="--extra postgres"
RUN useradd --create-home --uid 10001 app && mkdir /data && chown 10001 /data

# hadolint ignore=DL3008
RUN case "$UV_EXTRAS" in \
      *mysql*) apt-get update \
        && apt-get install -y --no-install-recommends libmariadb3 \
        && rm -rf /var/lib/apt/lists/* ;; \
    esac

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
# The service needs neither pip nor setuptools at runtime. Removing them also removes the
# vulnerable libraries that pip vendors, which image scanners report.
RUN pip uninstall --yes pip setuptools wheel

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    EXAMPLE_SERVER=wsgi \
    EXAMPLE_HOST=0.0.0.0 \
    EXAMPLE_PORT=8000 \
    EXAMPLE_DATA_DIR=/data \
    EXAMPLE_STATIC_ROOT=/app/staticfiles \
    EXAMPLE_DOCS_ENABLED=false

# Collect static files at build time. The values below are only needed to load the settings.
RUN EXAMPLE_SECRET_KEY=build-time-only EXAMPLE_ALLOWED_HOSTS=localhost \
    example-manage collectstatic --noinput

USER 10001
EXPOSE 8000
VOLUME /data
# The probe follows EXAMPLE_PORT. Its Host header is 127.0.0.1, so allow that host (see docs).
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD ["python", "-c", "import os, urllib.request as u; u.urlopen('http://127.0.0.1:%s/health' % os.environ['EXAMPLE_PORT'], timeout=2)"]
CMD ["example-serve"]
