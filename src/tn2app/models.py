import os.path
from functools import partial

from django.conf import settings
from django.contrib.auth.models import User as UserBase, UserManager as UserManagerBase
from django.contrib.auth.hashers import get_hasher
from django.db import models
from django.db.models import Max, Q
from django.urls import reverse
from django.utils.text import slugify

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
    wpdb_id = models.IntegerField(null=True)
    avatar = models.ImageField(
        upload_to=get_user_avatar_path,
        blank=True,
        verbose_name="Avatar"
    )
    display_name = models.CharField(max_length=60, blank=True, verbose_name="Pseudo")
    description = RichTextField(config_name='restricted', blank=True, verbose_name="Qui suis-je?")
    city = models.TextField(blank=True, verbose_name="Ville")
    website = models.URLField(blank=True, verbose_name="Site web")
    skill_level = models.CharField(
        max_length=20,
        blank=True,
        choices=SKILL_LEVEL_CHOICES,
        verbose_name="Niveau",
    )
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

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        limit_choices_to=Q(groups__name='Rédacteurs'),
    )
    slug = models.SlugField(max_length=255, unique=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_DRAFT)
    title = models.CharField(max_length=255)
    content = RichTextUploadingField()
    main_image = models.ImageField(blank=True)
    categories = models.ManyToManyField('ArticleCategory')
    creation_time = models.DateTimeField(auto_now_add=True)
    publish_time = models.DateTimeField(blank=True, null=True)

    objects = models.Manager()
    published = PublishedArticleManager()

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])


class ArticleCategory(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', args=[self.slug])


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


class ProjectCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


def get_project_image_path(instance, filename, slot):
    root, ext = os.path.splitext(filename)
    return 'projects/{}/img{}{}'.format(instance.id, slot, ext)

class Project(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='projects')
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(ProjectCategory)
    pattern_name = models.CharField(max_length=250, blank=True)
    pattern_url = models.URLField(max_length=250, blank=True)
    blog_post_url = models.URLField(max_length=250, blank=True)
    store_url = models.URLField(max_length=250, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)

    # baaah, it's not worth the extra indirection to create a model for project images.
    # Let's go low-tech and have 4 fields.
    image1 = models.ImageField(upload_to=partial(get_project_image_path, slot=1))
    image2 = models.ImageField(upload_to=partial(get_project_image_path, slot=2), blank=True)
    image3 = models.ImageField(upload_to=partial(get_project_image_path, slot=3), blank=True)
    image4 = models.ImageField(upload_to=partial(get_project_image_path, slot=4), blank=True)

    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ProjectVote')

    class Meta:
        ordering = ['-creation_time']

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.author, self.title)

    def get_absolute_url(self):
        return reverse('project_details', args=[self.id, self.get_slug()])

    def get_slug(self):
        return slugify(self.title)

    def get_images(self):
        return [self.image1, self.image2, self.image3, self.image4]


class ProjectVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    project = models.ForeignKey(Project)
    date_liked = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')

