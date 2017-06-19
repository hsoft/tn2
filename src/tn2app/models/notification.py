from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from django.utils.safestring import mark_safe

from ..util import href
from .user import UserProfile


class NotificationManager(models.Manager):
    def set_notification_flag(self, user_ids):
        UserProfile.objects.filter(user_id__in=user_ids).update(has_notifications=True)

    def notify_of_discussion_reply(self, comment):
        discussion = comment.target
        participant_ids = set(
            discussion.comments.distinct().order_by('user_id').values_list('user_id', flat=True)
        )
        participant_ids.add(discussion.author_id)
        participant_ids.discard(comment.user_id)
        self.bulk_create([
            Notification(
                user_id=participant_id,
                other_id=comment.user_id,
                type=Notification.TYPE_REPLY,
                target=comment,
            )
            for participant_id in participant_ids
        ])
        self.set_notification_flag(participant_ids)

    def notify_of_project_vote(self, vote):
        Notification.objects.create(
            user=vote.project.author,
            other=vote.user,
            type=Notification.TYPE_PROJECT_VOTE,
            target=vote.project,
        )
        self.set_notification_flag([vote.project.author.id])


class Notification(models.Model):
    class Meta:
        ordering = ('-time', )
        app_label = 'tn2app'

    TYPE_REPLY = 1
    TYPE_PROJECT_VOTE = 2

    TYPE_CHOICES = (
        (TYPE_REPLY, "Réponse dans une discussion"),
        (TYPE_PROJECT_VOTE, "Vote pour un projet"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications')
    other = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    time = models.DateTimeField(auto_now_add=True, db_index=True)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, db_index=True)
    target_content_type = models.ForeignKey(ContentType, null=True)
    target_object_id = models.PositiveIntegerField(null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    objects = NotificationManager()

    def get_message(self):
        if self.target:
            if self.type == self.TYPE_PROJECT_VOTE:
                target_name = "\"{}\"".format(self.target.title)
            else:
                target_name = "\"{}\"".format(self.target.target.title)
            target = href(self.target.get_absolute_url(), target_name)
        else:
            if self.type == self.TYPE_PROJECT_VOTE:
                target = "un projet qui a été supprimé"
            else:
                target = "une discussion qui a été supprimée"

        if self.type == self.TYPE_PROJECT_VOTE:
            msg = "{user} a aimé le projet {target} {time}."
        else:
            msg = "{user} a répondu à {target} {time}."
        return mark_safe(msg.format(
            user=self.other.profile.link(),
            target=target,
            time=naturaltime(self.time),
        ))
