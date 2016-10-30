from django.db import models
from django.urls import reverse

import bleach
from ckeditor.fields import RichTextField

ALLOWED_TAGS = ['b', 'i', 'u', 's', 'p', 'img', 'a', 'h2', 'h3', 'h4', 'h5', 'h6']

class Article(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    content = RichTextField()

    def clean(self):
        self.content = bleach.clean(self.content, tags=ALLOWED_TAGS)

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])

