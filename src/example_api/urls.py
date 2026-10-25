"""Version 1 of the API, served under ``/api/v1/``."""

from django.urls import URLPattern, URLResolver, path
from rest_framework.routers import SimpleRouter

from example_api import views

router = SimpleRouter()
router.register("notes", views.NoteViewSet, basename="note")

urlpatterns: list[URLPattern | URLResolver] = [
    path("hello/<str:name>/", views.HelloView.as_view(), name="hello"),
    path("whoami/", views.WhoAmIView.as_view(), name="whoami"),
    *router.urls,
]
