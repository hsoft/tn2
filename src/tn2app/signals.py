from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile, DiscussionComment, Notification

User = get_user_model()

@receiver(post_save, sender=User)
def user_was_saved(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        instance.profile.display_name = instance.username
        instance.profile.save()

@receiver(post_save, sender=DiscussionComment)
def discussioncomment_was_saved(sender, instance, created, **kwargs):
    if created:
        Notification.objects.notify_of_discussion_reply(instance)
