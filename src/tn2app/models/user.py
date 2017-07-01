import os.path

from django.conf import settings
from django.contrib.auth.models import User as UserBase
from django.db import models
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from ckeditor.fields import RichTextField

from ..util import PermissiveURLField


__all__ = ['User', 'UserProfile', 'get_user_avatar_path']

class User(UserBase):
    class Meta:
        proxy = True

    def favorite_projects(self):
        return self.liked_projects.filter(projectvote__favorite=True)


class UserProfileManager(models.Manager):
    def full_text_search(self, search_query):
        return self.filter(display_name__icontains=search_query)


def get_user_avatar_path(instance, filename):
    root, ext = os.path.splitext(filename)
    return 'avatars/{}{}'.format(instance.user.username, ext)

class UserProfile(models.Model):
    class Meta:
        app_label = 'tn2app'

    SKILL_LEVELS = (
        "Grand débutant",
        "Débutant",
        "Intermédiaire",
        "Avancé",
        "Professionnel",
    )
    SKILL_LEVEL_CHOICES = [(sl, sl) for sl in SKILL_LEVELS]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile',
    )
    wpdb_id = models.IntegerField(null=True, blank=True)
    avatar = models.ImageField(
        upload_to=get_user_avatar_path,
        blank=True,
        verbose_name="Avatar"
    )
    # We can't have a unique index because of legacy users having the same display_name.
    display_name = models.CharField(max_length=60, db_index=True, verbose_name="Pseudo")
    description = RichTextField(config_name='restricted', blank=True, verbose_name="Qui suis-je?")
    city = models.TextField(blank=True, verbose_name="Ville")
    website = PermissiveURLField(blank=True, verbose_name="Site web")
    skill_level = models.CharField(
        max_length=20,
        blank=True,
        choices=SKILL_LEVEL_CHOICES,
        verbose_name="Niveau",
    )
    sewing_machine = models.TextField(blank=True, verbose_name="MAC")
    description_for_articles = models.TextField(blank=True, verbose_name="Description Rédacteur")
    has_notifications = models.BooleanField(default=False)

    objects = UserProfileManager()

    def get_absolute_url(self):
        return reverse('user_profile', args=[self.user.username])

    def link(self):
        return mark_safe('<a href="{}">{}</a>'.format(
            self.get_absolute_url(),
            escape(self.display_name)
        ))
