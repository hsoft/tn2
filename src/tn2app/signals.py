from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile
from .util import sanitize_comment

User = get_user_model()

def comment_will_be_posted(sender, comment, request, **kwargs):
    comment.comment = sanitize_comment(comment.comment)

def comment_was_posted(sender, comment, request, **kwargs):
    if hasattr(comment.content_object, 'last_activity'):
        comment.content_object.last_activity = comment.submit_date
        comment.content_object.save()
    if hasattr(comment.content_object, 'last_poster'):
        comment.content_object.last_poster = comment.user
        comment.content_object.save()

@receiver(post_save, sender=User)
def user_was_saved(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        instance.profile.display_name = instance.username
        instance.profile.save()
