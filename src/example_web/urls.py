from django.urls import URLPattern, path

from example_web import views

urlpatterns: list[URLPattern] = [
    path("", views.index, name="index"),
    path("notes/", views.note_create, name="note-create"),
    path("notes/<int:pk>/delete/", views.note_delete, name="note-delete"),
]
