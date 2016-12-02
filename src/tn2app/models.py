from django.conf import settings
from django.db import models
from django.urls import reverse

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

from .util import sanitize_comment

class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    content = RichTextUploadingField()
    main_image = models.ImageField()
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])


class DiscussionGroup(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    private = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ('access_private_groups', "Accéder aux groupes privés"),
        )

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def get_absolute_url(self):
        return reverse('discussion_group', args=[self.slug])


class Discussion(models.Model):
    group = models.ForeignKey(DiscussionGroup, related_name='discussions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    slug = models.SlugField(max_length=255)
    title = models.CharField(max_length=255)
    content = RichTextField(config_name='restricted')
    creation_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'slug')

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def clean(self):
        self.content = sanitize_comment(self.content)

    def get_absolute_url(self):
        return reverse('discussion', args=[self.group.slug, self.slug])
