"""API views stay thin: validate input, call example_package or the ORM, return a serializer."""

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from example_api.auth import Principal
from example_api.serializers import HelloSerializer, NoteSerializer, WhoAmISerializer
from example_core.models import Note
from example_package import greet


class NoteViewSet(viewsets.ModelViewSet[Note]):
    """Create, read, update and delete notes."""

    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class HelloView(APIView):
    """Greet someone. Public: no authentication required."""

    permission_classes = [AllowAny]

    @extend_schema(responses=HelloSerializer, operation_id="hello")
    def get(self, request: Request, name: str) -> Response:
        try:
            message = greet(name)
        except ValueError as exc:
            # A fixed message: exception text is never echoed back to the caller.
            raise ValidationError("name must not be empty") from exc
        return Response({"message": message})


class WhoAmIView(APIView):
    """Show the caller. Protected according to ``EXAMPLE_API_AUTH_MODE``."""

    @extend_schema(responses=WhoAmISerializer, operation_id="whoami")
    def get(self, request: Request) -> Response:
        user = request.user
        if isinstance(user, Principal):
            return Response({"subject": user.subject, "method": user.method})
        if not user.is_authenticated:
            return Response({"subject": "anonymous", "method": "none"})
        return Response({"subject": user.get_username(), "method": "session"})
