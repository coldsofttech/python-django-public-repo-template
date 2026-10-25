"""URL configuration. Optional features register their routes only when they are enabled."""

from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from example_core import views

handler404 = "example_core.views.not_found"
handler500 = "example_core.views.error"


def build_urlpatterns(
    *,
    api: bool,
    ui: bool,
    admin_site: bool,
    docs: bool,
    admin_url: str = "admin/",
) -> list[URLPattern | URLResolver]:
    """Build the routes for the given set of features."""
    patterns: list[URLPattern | URLResolver] = [
        path("health", views.health, name="health"),
        path("ready", views.ready, name="ready"),
    ]
    if admin_site:
        patterns.append(path(admin_url, admin.site.urls))
    if api:
        patterns.append(path("api/v1/", include("example_api.urls")))
        if docs:
            patterns += [
                path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
                path(
                    "api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"
                ),
                path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
            ]
    if ui:
        patterns += [
            path("accounts/", include("django.contrib.auth.urls")),
            path("", include("example_web.urls")),
        ]
    return patterns


urlpatterns = build_urlpatterns(
    api=settings.API_ENABLED,
    ui=settings.UI_ENABLED,
    admin_site=settings.ADMIN_ENABLED,
    docs=settings.DOCS_ENABLED,
    admin_url=settings.ADMIN_URL,
)
