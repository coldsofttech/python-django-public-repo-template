# REST API

The optional REST API is built with [Django REST Framework](https://www.django-rest-framework.org/) and described by an OpenAPI 3 document. Turn it off with `EXAMPLE_API_ENABLED=false`: its routes then answer `404`.

The machine-readable contract is [openapi.json](openapi.json), generated from the code. While the server runs, interactive docs are at `/api/docs/` (Swagger UI) and `/api/redoc/`, and the live contract is at `/api/schema/`. The Docker image hides these by default (`EXAMPLE_DOCS_ENABLED=false`).

## Endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | none | Liveness probe. Never touches the database. |
| `GET` | `/ready` | none | Readiness probe. Returns 503 when the database does not answer. |
| `GET` | `/api/v1/hello/{name}/` | none | Greeting. Returns 400 for a blank name. |
| `GET` | `/api/v1/whoami/` | per auth mode | Shows who the caller is. |
| `GET`, `POST` | `/api/v1/notes/` | per auth mode | List (paginated with `limit`, at most 100, and `offset`) or create notes. |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/v1/notes/{id}/` | per auth mode | Read, change or delete a note. |

Versioned routes live under `/api/v1/`. Add `/api/v2/` as a new URL module when you need a breaking change, and keep `v1` running until callers have moved.

## Authentication

Choose a mode with `EXAMPLE_API_AUTH_MODE`. The default permission is "authenticated" for every mode except `none`.

| Mode | Caller sends | Use it for |
| --- | --- | --- |
| `none` | nothing | Local development. Every caller is anonymous. |
| `session` | the Django session cookie, plus the `X-CSRFToken` header on writes | The built-in UI and admin users. Default. |
| `api_key` | `X-API-Key: <key>` | Service-to-service calls. Keys come from `EXAMPLE_API_KEYS` and are compared in constant time. |
| `jwt` | `Authorization: Bearer <token>` | Tokens issued by an identity provider. Tokens must carry `exp` and `sub`. |

Notes:

- With `session`, an unauthenticated call gets `403` (the behavior of Django REST Framework for session auth). `api_key` and `jwt` answer `401` with a `WWW-Authenticate` header.
- Rotate API keys by listing the old and new key together, then removing the old one.
- For JWT in production, use an asymmetric algorithm such as `RS256` and set `EXAMPLE_JWT_KEY` to the provider public key, so the API can verify tokens but never sign them.
- Always serve the API over HTTPS.
- To make one view public, set `permission_classes = [AllowAny]` on it, as `HelloView` does.

## Errors

Every error uses the [problem details](https://www.rfc-editor.org/rfc/rfc9457) format with the content type `application/problem+json`:

```json
{"type": "about:blank", "title": "Bad Request", "status": 400, "detail": "Request validation failed.", "errors": {"title": ["This field may not be blank."]}}
```

Rate-limited requests get `429` with a `Retry-After` header. Unexpected errors return a bare `500` with no details, and the full error goes to the log with the request ID. Protections are described in [security](security.md).

## Adding an endpoint

1. Put the logic in `example_package` as a plain function. It must not know about HTTP.
2. Add a serializer in `example_api/serializers.py` and a view in `example_api/views.py` that calls the function, and register the route in `example_api/urls.py`.
3. Add tests with `APIClient` in `tests/`. Cover the real server in `tests/integration/` when it matters.
4. Regenerate the contract and commit it: `uv run python scripts/export_openapi.py`. CI fails if `openapi.json` is out of date, and the `api-compat` workflow fails if the change would break existing callers.
