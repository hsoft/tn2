from django import forms
from django.conf import settings
from django.utils.text import slugify

from ckeditor.widgets import CKEditorWidget

from ..models import Discussion
from ..util import dedupe_slug, sanitize_comment
from .base import BaseModelForm

__all__ = ['NewDiscussionForm', 'EditDiscussionForm', 'CommentForm']


class NewDiscussionForm(BaseModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content']

    def __init__(self, group, author, **kwargs):
        super().__init__(**kwargs)
        self.group = group
        self.author = author

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.group = self.group
        instance.author = self.author

        q = Discussion.objects.filter(group=self.group)
        instance.slug = dedupe_slug(slugify(instance.title), q)

        if commit:
            instance.save()

        return instance


class EditDiscussionForm(BaseModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content']


class CommentForm(forms.Form):
    comment = forms.CharField(
        label="Commentaire",
        widget=CKEditorWidget(config_name='restricted'),
        max_length=settings.COMMENT_MAX_LENGTH
    )

    def clean_comment(self):
        return sanitize_comment(self.cleaned_data['comment'])

