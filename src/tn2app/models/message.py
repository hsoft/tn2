from django.conf import settings
from django.db import models

from ckeditor.fields import RichTextField

from ..util import sanitize_comment

class Message(models.Model):
    class Meta:
        app_label = 'tn2app'
        ordering = ['-creation_time']

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='+',
        on_delete=models.CASCADE,
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='+',
        on_delete=models.CASCADE,
    )
    content = RichTextField(config_name='restricted', verbose_name="Message")
    creation_time = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return "{}: {} -> {}".format(self.creation_time, self.from_user, self.to_user)

    def clean(self):
        self.content = sanitize_comment(self.content)

