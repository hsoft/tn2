from django.db import models

from ckeditor.fields import RichTextField


__all__ = ['PageContents']

class PageContents(models.Model):
    class Meta:
        app_label = 'tn2app'

    key = models.CharField(max_length=30, unique=True)
    contents = RichTextField()

    def __str__(self):
        return self.key


