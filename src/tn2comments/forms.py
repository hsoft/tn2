from django import forms
from django_comments.forms import CommentForm, COMMENT_MAX_LENGTH
from ckeditor.widgets import CKEditorWidget

from .util import sanitize_comment

class CommentFormOverride(CommentForm):
    comment = forms.CharField(
        label="Commentaire",
        widget=CKEditorWidget(config_name='restricted'),
        max_length=COMMENT_MAX_LENGTH
    )

    def clean_comment(self):
        return sanitize_comment(self.cleaned_data['comment'])

