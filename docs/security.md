# Security

What the template protects against out of the box, what it leaves to your infrastructure, and how issues are found.

## Built into the app

| Protection | How | Setting |
| --- | --- | --- |
| Safe defaults | `DEBUG` is off, `SECRET_KEY` and `ALLOWED_HOSTS` are required, and `manage.py check --deploy` must pass in CI | `EXAMPLE_DEBUG`, `EXAMPLE_SECRET_KEY`, `EXAMPLE_ALLOWED_HOSTS` |
| HTTPS | Redirect to HTTPS, secure cookies and HSTS (one year, including subdomains). Probes are exempt from the redirect. | `EXAMPLE_HTTPS`, `EXAMPLE_BEHIND_PROXY` |
| API authentication | Session, API key or JWT ([details](api.md)) | `EXAMPLE_API_AUTH_MODE` |
| CSRF | Django CSRF protection on forms and session-authenticated API writes | `EXAMPLE_CSRF_TRUSTED_ORIGINS` |
| Rate limiting | Fixed window per client address, `429` with `Retry-After` and `X-RateLimit-*` headers. Probes and static files are exempt. | `EXAMPLE_RATE_LIMIT_PER_MINUTE` (default 120, `0` turns it off) |
| Request size limit | Bodies above the limit are refused | `EXAMPLE_MAX_BODY_BYTES` (default 1 MiB) |
| Security headers | `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Cross-Origin-Opener-Policy`, a strict `Content-Security-Policy` for the API and a same-origin one for the UI, and `Cache-Control: no-store` on `/api/` | none |
| Host allow-list | Django rejects unknown `Host` headers | `EXAMPLE_ALLOWED_HOSTS` |
| CORS | Off until you list origins | `EXAMPLE_CORS_ORIGINS` |
| Smaller attack surface | The API, UI, admin and API docs can each be switched off, and the admin can be moved. The Docker image hides the API docs. | `EXAMPLE_*_ENABLED`, `EXAMPLE_ADMIN_URL` |
| Safe errors | Problem details responses; 500 errors never expose details or stack traces | none |
| Secrets | Read from the environment, never logged; API keys compared in constant time | none |
| Container | Non-root user, slim base image, no pip in the final image | none |

Rate limiting counts in Django cache, so each instance enforces its own limit unless `CACHE_URL` points at a shared cache such as Redis. Behind a proxy, set `EXAMPLE_BEHIND_PROXY` and `EXAMPLE_PROXY_COUNT` so the limiter sees real client addresses (see [deployment](deployment.md)). The admin and the API docs pages load their own scripts, so they do not get a Content-Security-Policy from the app.

For stricter login protection (lockout after repeated failures), add a package such as `django-axes`, and use two-factor authentication for staff accounts.

## Left to your infrastructure

HTTPS and certificates, request timeouts, connection limits, a web application firewall, and size limits for chunked uploads belong to the reverse proxy or load balancer.

## Automated checks

| Check | Where | What it finds |
| --- | --- | --- |
| `manage.py check --deploy` | `ci` | Unsafe production settings |
| `makemigrations --check` | `ci` | Model changes without a migration |
| Ruff `S` and `DJ` rules | pre-commit and `ci` | Insecure Python and Django patterns |
| gitleaks | pre-commit and `ci` | Committed secrets |
| CodeQL | GitHub default setup | Code vulnerabilities |
| Dependency review | `dependency-review.yml` | Vulnerable dependencies added by a pull request |
| pip-audit | `audit.yml`, weekly | Advisories published against locked dependencies |
| Semgrep | `security.yml` | Python, Django, OWASP Top 10, Dockerfile and workflow issues |
| Hadolint | `security.yml` | Dockerfile mistakes and bad practices |
| Trivy | `security.yml` | Known vulnerabilities (high and critical) in the built image |
| Schemathesis | `tests/integration` | Server errors for any request the OpenAPI document allows |
| oasdiff | `api-compat.yml` | Changes that break existing API callers |

The `security.yml` jobs upload SARIF, so results appear under **Security > Code scanning** on GitHub. They run on pull requests, on pushes to `main` and weekly, and they are not part of the required `ci` check, so a newly published advisory does not block unrelated work. To make one required, add its job name to the branch ruleset.

To suppress a false positive, prefer a narrow, commented exception: `# nosemgrep: <rule-id>` for Semgrep, a `.trivyignore` entry with a reason for Trivy, or `# hadolint ignore=DLxxxx` for Hadolint.

## Reporting a vulnerability

See [SECURITY.md](../SECURITY.md).
