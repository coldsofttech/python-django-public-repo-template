"""Django settings, read from ``EXAMPLE_*`` variables, ``DATABASE_URL`` and ``CACHE_URL``.

A ``.env`` file in the working directory is read too (see ``.env.example``). Nothing here is
specific to one environment: development turns on ``EXAMPLE_DEBUG``, production leaves it off.
"""

from pathlib import Path

import django_stubs_ext
import environ
from django.core.exceptions import ImproperlyConfigured

from example_package import __version__

# Lets generic types such as ModelAdmin[Note] be written at runtime (for type checkers).
django_stubs_ext.monkeypatch()

env = environ.Env()
_env_file = Path.cwd() / ".env"
if _env_file.is_file():
    environ.Env.read_env(str(_env_file))

# --- Core -----------------------------------------------------------------------------------------

DEBUG = env.bool("EXAMPLE_DEBUG", default=False)

SECRET_KEY = env.str("EXAMPLE_SECRET_KEY", default="")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("EXAMPLE_SECRET_KEY is required when EXAMPLE_DEBUG is off.")
    SECRET_KEY = "insecure-development-key-do-not-use-in-production"  # noqa: S105

ALLOWED_HOSTS = env.list(
    "EXAMPLE_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "[::1]", "testserver"] if DEBUG else [],
)
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured("EXAMPLE_ALLOWED_HOSTS is required when EXAMPLE_DEBUG is off.")

CSRF_TRUSTED_ORIGINS = env.list("EXAMPLE_CSRF_TRUSTED_ORIGINS", default=[])
CORS_ALLOWED_ORIGINS = env.list("EXAMPLE_CORS_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = env.bool("EXAMPLE_CORS_ALLOW_CREDENTIALS", default=False)
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "x-api-key",
    "x-csrftoken",
    "x-request-id",
]

# Optional features. Routes for a disabled feature are not registered at all.
ADMIN_ENABLED = env.bool("EXAMPLE_ADMIN_ENABLED", default=True)
ADMIN_URL = env.str("EXAMPLE_ADMIN_URL", default="admin/").strip("/") + "/"
API_ENABLED = env.bool("EXAMPLE_API_ENABLED", default=True)
UI_ENABLED = env.bool("EXAMPLE_UI_ENABLED", default=True)
DOCS_ENABLED = env.bool("EXAMPLE_DOCS_ENABLED", default=True)

# --- Application definition -----------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "example_core",
    "example_api",
    "example_web",
]

MIDDLEWARE = [
    "example_core.middleware.RequestIdMiddleware",
    "example_core.middleware.SecurityHeadersMiddleware",
    "example_core.middleware.RateLimitMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "example_project.urls"
WSGI_APPLICATION = "example_project.wsgi.application"
ASGI_APPLICATION = "example_project.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Database and cache ---------------------------------------------------------------------------
# DATABASE_URL accepts any scheme django-environ knows, for example:
#   sqlite:///db.sqlite3   postgres://user:pass@host:5432/name   mysql://user:pass@host:3306/name
#   oracle://user:pass@host:1521/service
# For other databases install the Django backend and set DATABASE_URL (see docs/database.md).

_data_dir = Path(env.str("EXAMPLE_DATA_DIR", default=str(Path.cwd())))
DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{_data_dir / 'db.sqlite3'}")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("EXAMPLE_DB_CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# A shared cache (for example Redis) makes rate limits and sessions consistent across instances.
CACHES = {"default": env.cache("CACHE_URL", default="locmemcache://")}

# --- Authentication -------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# --- Internationalization -------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static files ---------------------------------------------------------------------------------

ROOT_PATH = env.str("EXAMPLE_ROOT_PATH", default="").rstrip("/")
if ROOT_PATH:
    FORCE_SCRIPT_NAME = ROOT_PATH
STATIC_URL = "static/"
STATIC_URL_PATH = "/static/"  # used by the rate limiter to skip static files
STATIC_ROOT = Path(env.str("EXAMPLE_STATIC_ROOT", default=str(Path.cwd() / "staticfiles")))
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

# --- HTTPS, proxies and security ------------------------------------------------------------------
# `manage.py check --deploy` reports anything that is still unsafe.

HTTPS = env.bool("EXAMPLE_HTTPS", default=not DEBUG)
BEHIND_PROXY = env.bool("EXAMPLE_BEHIND_PROXY", default=False)
PROXY_COUNT = env.int("EXAMPLE_PROXY_COUNT", default=1 if BEHIND_PROXY else 0)
if BEHIND_PROXY:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "no-referrer"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
# Larger request bodies are refused (400). Chunked uploads should also be limited at the proxy.
DATA_UPLOAD_MAX_MEMORY_SIZE = env.int("EXAMPLE_MAX_BODY_BYTES", default=1_048_576)

if HTTPS:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [r"^health$", r"^ready$"]  # probes usually use plain HTTP
    SECURE_HSTS_SECONDS = 31_536_000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# HSTS preload is hard to undo, so it is opt-in. Without it, Django's reminder is silenced.
SECURE_HSTS_PRELOAD = env.bool("EXAMPLE_HSTS_PRELOAD", default=False)
SILENCED_SYSTEM_CHECKS = [] if SECURE_HSTS_PRELOAD else ["security.W021"]

RATE_LIMIT_PER_MINUTE = env.int("EXAMPLE_RATE_LIMIT_PER_MINUTE", default=120)

# --- REST API (Django REST Framework) -------------------------------------------------------------
# EXAMPLE_API_AUTH_MODE is one of: none, session, api_key, jwt.

API_AUTH_MODE = env.str("EXAMPLE_API_AUTH_MODE", default="session")
API_KEYS = env.list("EXAMPLE_API_KEYS", default=[])
JWT_KEY = env.str("EXAMPLE_JWT_KEY", default="")
JWT_ALGORITHM = env.str("EXAMPLE_JWT_ALGORITHM", default="HS256")
JWT_AUDIENCE = env.str("EXAMPLE_JWT_AUDIENCE", default="") or None
JWT_ISSUER = env.str("EXAMPLE_JWT_ISSUER", default="") or None

_AUTH_CLASSES = {
    "none": [],
    "session": ["rest_framework.authentication.SessionAuthentication"],
    "api_key": ["example_api.auth.ApiKeyAuthentication"],
    "jwt": ["example_api.auth.JWTAuthentication"],
}
if API_AUTH_MODE not in _AUTH_CLASSES:
    raise ImproperlyConfigured(
        f"EXAMPLE_API_AUTH_MODE must be one of {', '.join(_AUTH_CLASSES)}, not {API_AUTH_MODE!r}."
    )
if API_AUTH_MODE == "api_key" and not API_KEYS:
    raise ImproperlyConfigured("EXAMPLE_API_KEYS is required when the auth mode is api_key.")
if API_AUTH_MODE == "jwt" and not JWT_KEY:
    raise ImproperlyConfigured("EXAMPLE_JWT_KEY is required when the auth mode is jwt.")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": _AUTH_CLASSES[API_AUTH_MODE],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny"
        if API_AUTH_MODE == "none"
        else "rest_framework.permissions.IsAuthenticated"
    ],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_PAGINATION_CLASS": "example_api.pagination.BoundedLimitOffsetPagination",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "example_api.errors.problem_exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "example-api",
    "DESCRIPTION": "Example HTTP API built on **example_package**.",
    "VERSION": __version__,
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

# --- Logging --------------------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "example_core.logs.JsonFormatter"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {
        "handlers": ["console"],
        "level": env.str("EXAMPLE_LOG_LEVEL", default="INFO").upper(),
    },
}
