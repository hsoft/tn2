from django import forms
from django.utils.text import slugify

from django_comments.models import Comment
from django_comments.forms import COMMENT_MAX_LENGTH
from ckeditor.widgets import CKEditorWidget

from .models import Discussion
from .util import dedupe_slug


class NewDiscussionForm(forms.ModelForm):
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


class EditDiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content']


class EditCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

    comment = forms.CharField(
        label="Commentaire",
        widget=CKEditorWidget(config_name='restricted'),
        max_length=COMMENT_MAX_LENGTH
    )
