from django import forms
from .models import Comment

class CommentSubmitForm (forms.Form):
    commentaire = forms.CharField(
        widget=forms.Textarea,
        label="Commentaire",
        required=True)

    class Meta:
        model = Comment
        fields = {"commentaire", }
