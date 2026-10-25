# Deployment

The app listens on a host and port. Your domain name, DNS and HTTPS certificates are set up in front of it, by a reverse proxy, load balancer or platform ingress.

## Choosing a server

`example-serve` starts the server named by `EXAMPLE_SERVER`:

| Value | Server | Interface | Notes |
| --- | --- | --- | --- |
| `wsgi` (default) | gunicorn | WSGI | The proven default. Linux and macOS only. |
| `asgi` | uvicorn | ASGI | Needed for async views, WebSockets or streaming. Runs everywhere, including Windows. |

Both serve the same code. Use `example-manage runserver` only for development. The entry points are `example_project.wsgi:application` and `example_project.asgi:application`, so any WSGI or ASGI server (for example Hypercorn or Daphne) works too.

```bash
EXAMPLE_SERVER=asgi EXAMPLE_PORT=8000 uv run example-serve
```

## Where each thing is configured

| What | Where |
| --- | --- |
| Domain name and DNS | Your DNS provider, pointing at the proxy or load balancer |
| HTTPS certificate | The proxy or load balancer (Caddy, nginx, Traefik, a cloud load balancer) |
| Port the app listens on | `EXAMPLE_PORT` (default `8000`) |
| Interface | `EXAMPLE_HOST` (`127.0.0.1` by default, `0.0.0.0` in the Docker image) |
| Accepted domains | `EXAMPLE_ALLOWED_HOSTS` |
| Pages and forms from other origins | `EXAMPLE_CSRF_TRUSTED_ORIGINS` |
| Browser origins allowed to call the API | `EXAMPLE_CORS_ORIGINS` |

## Behind a reverse proxy

A typical setup is `client -> proxy (HTTPS, your domain) -> app (plain HTTP, private network)`.

1. Set `EXAMPLE_ALLOWED_HOSTS` to your domain, and include `127.0.0.1` so the container health check works.
2. Set `EXAMPLE_BEHIND_PROXY=true`. Django then trusts `X-Forwarded-Proto` to know the request was HTTPS, and rate limiting reads the client address from `X-Forwarded-For`. Only do this when every request really passes through the proxy, and make sure the proxy overwrites those headers.
3. Set `EXAMPLE_PROXY_COUNT` to the number of proxies in front of the app if it is not 1.
4. Set `EXAMPLE_FORWARDED_ALLOW_IPS` to the proxy address so the server accepts its forwarded headers.
5. Add the origin of your site to `EXAMPLE_CSRF_TRUSTED_ORIGINS`, for example `https://example.com`.

Example Caddyfile (Caddy gets and renews the certificate for you):

```text
example.com {
    reverse_proxy 127.0.0.1:8000
}
```

## Serving under a sub-path

If the proxy exposes the app at `https://example.com/myapp/` and strips the prefix, set `EXAMPLE_ROOT_PATH=/myapp`. URLs, static files and redirects then include the prefix.

## Static files

WhiteNoise serves static files from the app itself, with compression and cache-friendly names, so no separate file server is needed. Run `example-manage collectstatic --noinput` once at build time (the Dockerfile does this). Serve them from a CDN instead if you prefer.

## Docker

```bash
docker build -t myapp .
docker run -p 8000:8000 -e EXAMPLE_SECRET_KEY=... -e EXAMPLE_ALLOWED_HOSTS=localhost,127.0.0.1 \
  -e EXAMPLE_HTTPS=false myapp
```

The image runs as a non-root user, has no pip, and uses `EXAMPLE_SERVER=wsgi` unless you change it. SQLite data goes to the `/data` volume. For a real database set `DATABASE_URL`. Pick the database drivers at build time (see [database](database.md)).

`compose.yaml` runs the app with PostgreSQL and a one-off migration step for local use: copy `.env.example` to `.env`, set `EXAMPLE_SECRET_KEY`, then `docker compose up --build`.

## Health probes

| Probe | Path | Meaning |
| --- | --- | --- |
| Liveness | `/health` | The process is running. Restart the container if it fails. |
| Readiness | `/ready` | The database answers. Route traffic only when this passes. |

Both are exempt from rate limiting and from the HTTPS redirect. The Docker image already has a health check that follows `EXAMPLE_PORT`.

## Scaling and shutdown

Run more containers behind the load balancer instead of more workers in one container. Sessions are stored in the database, so any instance can answer any request. Rate limits are counted per process unless `CACHE_URL` points at a shared cache such as Redis.

On shutdown the server stops accepting connections and gives in-flight requests `EXAMPLE_SHUTDOWN_TIMEOUT` seconds (default 10) to finish. Keep the termination grace period of your platform longer than that. Run `example-manage migrate` as a separate step before starting a new version.

## Not covered by the app

HTTPS and certificates, request timeouts, connection limits, a web application firewall, and size limits for chunked uploads belong to the proxy or load balancer. See [security](security.md) for what the app enforces itself.
