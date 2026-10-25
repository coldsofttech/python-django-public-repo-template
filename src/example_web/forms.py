from django import forms

from example_core.models import Note


class NoteForm(forms.ModelForm[Note]):
    class Meta:
        model = Note
        fields = ["title", "body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}
