from django import forms
from django.utils.text import slugify

from django_comments.models import Comment
from django_comments.forms import COMMENT_MAX_LENGTH
from ckeditor.widgets import CKEditorWidget

from .models import UserProfile, Discussion, Project
from .util import dedupe_slug


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)


class UserProfileForm(BaseModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'display_name', 'description', 'city', 'website', 'skill_level', 'sewing_machine',
            'avatar',
        ]
        widgets = {
            'city': forms.TextInput(),
            'sewing_machine': forms.TextInput(),
        }


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


class EditCommentForm(BaseModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

    comment = forms.CharField(
        label="Commentaire",
        widget=CKEditorWidget(config_name='restricted'),
        max_length=COMMENT_MAX_LENGTH
    )

class NewProjectForm(BaseModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'category', 'description', 'pattern_name', 'pattern_url', 'blog_post_url',
            'image1', 'image2', 'image3', 'image4', 'store_url'
        ]

    def __init__(self, author, **kwargs):
        super().__init__(**kwargs)
        self.author = author

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.author = self.author

        if commit:
            instance.save()

        return instance


