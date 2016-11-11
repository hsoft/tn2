from django import forms
from django.utils.text import slugify

from .models import Discussion, Article
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

class NewArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'main_image']

    def __init__(self, author, **kwargs):
        super().__init__(**kwargs)
        self.author = author

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.author = self.author

        q = Article.objects
        instance.slug = dedupe_slug(slugify(instance.title), q)

        if commit:
            instance.save()

        return instance

class EditArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'main_image']

