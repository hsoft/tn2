import os.path

from django.conf import settings
from django.contrib.auth.models import User as UserBase, UserManager as UserManagerBase
from django.contrib.auth.hashers import get_hasher
from django.db import models
from django.db.models import Max
from django.urls import reverse

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

from wordpress.models import WpV2Users

from .util import sanitize_comment, nonone

class UserManager(UserManagerBase):
    def get_from_wpuser_id(self, wpuser_id):
        try:
            return self.get(profile__wpdb_id=wpuser_id)
        except self.model.DoesNotExist:
            pass
        wpuser = WpV2Users.objects.get(id=wpuser_id)
        hasher = get_hasher('phpass')
        user = self.create(
            username=wpuser.user_login,
            email=wpuser.user_email,
            password=hasher.from_orig(wpuser.user_pass),
            is_active=True,
        )
        UserProfile.objects.create(user=user, wpdb_id=wpuser.id)
        return user

class User(UserBase):
    objects = UserManager()

    class Meta:
        proxy = True


def get_user_avatar_path(instance, filename):
    root, ext = os.path.splitext(filename)
    return 'avatars/{}{}'.format(instance.user.username, ext)

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile',
    )
    wpdb_id = models.IntegerField(null=True)
    avatar = models.ImageField(upload_to=get_user_avatar_path, blank=True)
    display_name = models.CharField(max_length=60, blank=True, verbose_name="Pseudo")
    description = models.TextField(blank=True, verbose_name="Qui suis-je?")
    city = models.TextField(blank=True, verbose_name="Ville")
    website = models.URLField(blank=True, verbose_name="Site web")
    skill_level = models.CharField(max_length=20, blank=True, verbose_name="Niveau")
    sewing_machine = models.TextField(blank=True, verbose_name="MAC")

    def get_absolute_url(self):
        return reverse('user_profile', args=[self.user.username])


class PublishedArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Article.STATUS_PUBLISHED)

class Article(models.Model):
    STATUS_DRAFT = 0
    STATUS_REVISION = 1
    STATUS_PUBLISHED = 2
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Brouillon"),
        (STATUS_REVISION, "Révision"),
        (STATUS_PUBLISHED, "Publié"),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_DRAFT)
    title = models.CharField(max_length=255)
    content = RichTextUploadingField()
    main_image = models.ImageField(blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    publish_time = models.DateTimeField(blank=True, null=True)

    objects = models.Manager()
    published = PublishedArticleManager()

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])


class DiscussionGroup(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    private = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ('access_private_groups', "Accéder aux groupes privés"),
        )

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def get_absolute_url(self):
        return reverse('discussion_group', args=[self.slug])

    def last_activity(self):
        return nonone(self.discussions.aggregate(Max('last_activity'))['last_activity__max'], '-')


class Discussion(models.Model):
    group = models.ForeignKey(DiscussionGroup, related_name='discussions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    slug = models.SlugField(max_length=255)
    title = models.CharField(max_length=255)
    content = RichTextField(config_name='restricted')
    creation_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now_add=True)
    is_locked = models.BooleanField(default=False)
    is_sticky = models.BooleanField(default=False)

    class Meta:
        unique_together = ('group', 'slug')

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def clean(self):
        self.content = sanitize_comment(self.content)

    def get_absolute_url(self):
        return reverse('discussion', args=[self.group.slug, self.slug])
