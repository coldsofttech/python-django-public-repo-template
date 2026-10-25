from django.db import models


class Note(models.Model):
    """Example model. It shows migrations, the admin, the API and the UI working together."""

    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return self.title
