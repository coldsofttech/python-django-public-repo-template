from rest_framework import serializers

from example_core.models import Note


class NoteSerializer(serializers.ModelSerializer[Note]):
    class Meta:
        model = Note
        fields = ["id", "title", "body", "created_at"]
        read_only_fields = ["id", "created_at"]


class HelloSerializer(serializers.Serializer[dict[str, str]]):
    message = serializers.CharField()


class WhoAmISerializer(serializers.Serializer[dict[str, str]]):
    subject = serializers.CharField(help_text="Identity of the caller.")
    method = serializers.CharField(help_text="How the caller was authenticated.")
