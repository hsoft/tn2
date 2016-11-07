import itertools

from django import forms
from django.utils.text import slugify

from .models import Discussion

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

        max_length = Discussion._meta.get_field('slug').max_length
        # Never going to be above 1000 conflicts...
        slug = slug_orig = slugify(instance.title)[:max_length-4]
        for i in itertools.count(1):
            if Discussion.objects.filter(group=self.group, slug=slug).exists():
                slug = "{}-{}".format(slug_orig, i)
            else:
                break
        instance.slug = slug

        if commit:
            instance.save()

        return instance

