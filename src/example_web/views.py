"""Server-rendered pages. HTMX swaps small fragments without a full page reload."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from example_core.models import Note
from example_package import greet
from example_web.forms import NoteForm


def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


def index(request: HttpRequest) -> HttpResponse:
    """Landing page. Signed-in users also see their notes."""
    notes = Note.objects.all() if request.user.is_authenticated else Note.objects.none()
    context = {
        "greeting": greet(request.user.get_username() or "world"),
        "notes": notes,
        "form": NoteForm(),
    }
    return render(request, "example_web/index.html", context)


@login_required
@require_http_methods(["POST"])
def note_create(request: HttpRequest) -> HttpResponse:
    form = NoteForm(request.POST)
    if not form.is_valid():
        return render(request, "example_web/_form.html", {"form": form}, status=422)
    note = form.save()
    if _is_htmx(request):
        context = {"note": note, "form": NoteForm()}
        return render(request, "example_web/_created.html", context, status=201)
    return redirect("index")


@login_required
@require_POST
def note_delete(request: HttpRequest, pk: int) -> HttpResponse:
    get_object_or_404(Note, pk=pk).delete()
    if _is_htmx(request):
        return HttpResponse(status=200)
    return redirect("index")
