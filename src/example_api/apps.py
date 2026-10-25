from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "example_api"

    def ready(self) -> None:
        # Registers how the custom authentication classes appear in the OpenAPI document.
        from example_api import schema  # noqa: F401
