from django import forms
from django_comments.forms import CommentForm, COMMENT_MAX_LENGTH
from ckeditor.widgets import CKEditorWidget

class CommentFormOverride(CommentForm):
    comment = forms.CharField(
        label="Commentaire",
        widget=CKEditorWidget(config_name='restricted'),
        max_length=COMMENT_MAX_LENGTH
    )
