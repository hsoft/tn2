from django.conf import settings
from django.db import models
from django.urls import reverse


class AbstractComment(models.Model):
    class Meta:
        abstract = True
        ordering = ('submit_date', )
        app_label = 'tn2app'

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    submit_date = models.DateTimeField(auto_now_add=True, db_index=True)
    comment = models.TextField(max_length=settings.COMMENT_MAX_LENGTH)

    def get_edit_url(self):
        model_name = self.target._meta.model_name
        return reverse('comment_edit', kwargs={'model': model_name, 'comment_pk': self.id})


class CommentableMixin:
    def get_submit_comment_url(self):
        model_name = self._meta.model_name
        return reverse('comment_add', args=[model_name, self.id])

