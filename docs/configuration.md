# Configuration

Everything is configured with environment variables, so the same image runs in development, CI and production. For local work you can put them in a `.env` file in the working directory (start from `.env.example`). Names are prefixed `EXAMPLE_`, except the standard `DATABASE_URL` and `CACHE_URL`. List values are comma separated.

Settings are read in `src/example_project/settings.py`. Mistakes stop the app at startup with a clear message instead of failing on the first request.

## Core

| Variable | Default | Description |
| --- | --- | --- |
| `EXAMPLE_DEBUG` | `false` | Development mode. Never enable it in production. |
| `EXAMPLE_SECRET_KEY` | | **Required** unless `EXAMPLE_DEBUG` is on. At least 50 characters, random. |
| `EXAMPLE_ALLOWED_HOSTS` | | **Required** unless `EXAMPLE_DEBUG` is on. Your domains, for example `example.com,www.example.com`. |
| `EXAMPLE_LOG_LEVEL` | `INFO` | Log level. Logs are JSON, one object per line, with a request ID. |
| `EXAMPLE_DATA_DIR` | working directory | Where the default SQLite file lives. |
| `EXAMPLE_STATIC_ROOT` | `./staticfiles` | Where `collectstatic` puts files. |

## Optional features

Routes for a disabled feature are not registered, so they answer `404`.

| Variable | Default | Description |
| --- | --- | --- |
| `EXAMPLE_API_ENABLED` | `true` | The REST API under `/api/v1/`. |
| `EXAMPLE_UI_ENABLED` | `true` | The built-in web pages and sign-in. |
| `EXAMPLE_ADMIN_ENABLED` | `true` | The Django admin. |
| `EXAMPLE_ADMIN_URL` | `admin/` | Where the admin lives. Move it to make scanning harder. |
| `EXAMPLE_DOCS_ENABLED` | `true` | `/api/docs/`, `/api/redoc/` and `/api/schema/`. The Docker image sets `false`. |

## Database and cache

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | SQLite file in `EXAMPLE_DATA_DIR` | See [database](database.md). |
| `EXAMPLE_DB_CONN_MAX_AGE` | `60` | Seconds to keep database connections open. |
| `CACHE_URL` | `locmemcache://` | Cache used for rate limiting. Use a shared cache such as `rediscache://host:6379/1` with several instances. |

## Servers

Used by `example-serve` (see [deployment](deployment.md)).

| Variable | Default | Description |
| --- | --- | --- |
| `EXAMPLE_SERVER` | `wsgi` | `wsgi` (gunicorn) or `asgi` (uvicorn). |
| `EXAMPLE_HOST` | `127.0.0.1` | Interface to listen on. The Docker image sets `0.0.0.0`. |
| `EXAMPLE_PORT` | `8000` | Port to listen on. |
| `EXAMPLE_WORKERS` | `1` | Server processes. Prefer more containers. |
| `EXAMPLE_SHUTDOWN_TIMEOUT` | `10` | Seconds to let requests finish on shutdown. |
| `EXAMPLE_FORWARDED_ALLOW_IPS` | `127.0.0.1` | Proxy addresses whose `X-Forwarded-*` headers the server trusts. |

## HTTPS, proxies and security

| Variable | Default | Description |
| --- | --- | --- |
| `EXAMPLE_HTTPS` | on unless debugging | Secure cookies, redirect HTTP to HTTPS (not for `/health` and `/ready`) and HSTS. Turn off only for plain-HTTP local runs. |
| `EXAMPLE_BEHIND_PROXY` | `false` | Trust `X-Forwarded-Proto` to know a request was HTTPS. Set when a proxy terminates TLS. |
| `EXAMPLE_PROXY_COUNT` | `1` behind a proxy, else `0` | How many trusted proxies sit in front, used to find the real client address for rate limiting. |
| `EXAMPLE_HSTS_PRELOAD` | `false` | Opt in to HSTS preload. It is hard to undo. |
| `EXAMPLE_CSRF_TRUSTED_ORIGINS` | | Origins allowed to submit forms, such as `https://example.com`. Needed behind a proxy on another origin. |
| `EXAMPLE_CORS_ORIGINS` | | Browser origins allowed to call the API, such as a separate frontend. |
| `EXAMPLE_CORS_ALLOW_CREDENTIALS` | `false` | Allow cookies on cross-origin API calls. |
| `EXAMPLE_ROOT_PATH` | | Path prefix when a proxy serves the app under a sub-path, such as `/myapp`. |
| `EXAMPLE_RATE_LIMIT_PER_MINUTE` | `120` | Requests per client address per minute. `0` turns the limit off. |
| `EXAMPLE_MAX_BODY_BYTES` | `1048576` | Largest accepted request body. |

## API authentication

| Variable | Default | Description |
| --- | --- | --- |
| `EXAMPLE_API_AUTH_MODE` | `session` | `none`, `session`, `api_key` or `jwt`. See [API](api.md). |
| `EXAMPLE_API_KEYS` | | Accepted keys for `api_key` mode. |
| `EXAMPLE_JWT_KEY` | | Key used to verify tokens in `jwt` mode. |
| `EXAMPLE_JWT_ALGORITHM` | `HS256` | Token signing algorithm. |
| `EXAMPLE_JWT_AUDIENCE` | | Required `aud` claim, if set. |
| `EXAMPLE_JWT_ISSUER` | | Required `iss` claim, if set. |

## Checking a production configuration

```bash
EXAMPLE_SECRET_KEY=... EXAMPLE_ALLOWED_HOSTS=example.com \
  uv run example-manage check --deploy --fail-level WARNING
```

CI runs this with a production-like configuration, so unsafe defaults cannot creep in.
