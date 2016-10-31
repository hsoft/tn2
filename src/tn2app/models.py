from django.db import models
from django.urls import reverse

import bleach
from ckeditor.fields import RichTextField

ALLOWED_TAGS_RESTRICTED = ['b', 'i', 'u', 's', 'p', 'img', 'a', 'em', 'strong']
ALLOWED_TAGS_PERMISSIVE = ALLOWED_TAGS_RESTRICTED + ['h2', 'h3', 'h4', 'h5', 'h6']

class Article(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    content = RichTextField()
    main_image = models.ImageField()

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def clean(self):
        self.content = bleach.clean(self.content, tags=ALLOWED_TAGS_PERMISSIVE)

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])


class DiscussionGroup(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    private = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def get_absolute_url(self):
        return reverse('discussion_group', args=[self.slug])


class Discussion(models.Model):
    group = models.ForeignKey(DiscussionGroup, related_name='discussions')
    slug = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    content = RichTextField(config_name='restricted')
    creation_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'slug')

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def clean(self):
        self.content = bleach.clean(self.content, tags=ALLOWED_TAGS_RESTRICTED)

    def get_absolute_url(self):
        return reverse('discussion', args=[self.group.slug, self.slug])
