import datetime
import html
import os.path
from functools import partial

from django.conf import settings
from django.contrib.auth.models import User as UserBase, UserManager as UserManagerBase
from django.contrib.auth.hashers import get_hasher
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db import models
from django.db.models import Max, Q, Count
from django.template.defaultfilters import striptags, truncatewords
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import slugify

from PIL import Image
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

from wordpress.models import WpV2Users

from .util import nonone, fa_str, embed_videos, sanitize_comment

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


class AbstractComment(models.Model):
    class Meta:
        abstract = True
        ordering = ('submit_date', )

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


class ArticleManager(models.Manager):
    def full_text_search(self, search_query):
        # Postgres full-text index for this search added in migration 0031
        sv = SearchVector('title', 'content', config='french')
        return self.annotate(search=sv)\
            .annotate(rank=SearchRank(sv, search_query))\
            .filter(search=search_query, status=Article.STATUS_PUBLISHED)\
            .order_by('-rank')


class PublishedArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Article.STATUS_PUBLISHED)

class Article(CommentableMixin, models.Model):
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
    subtitle = models.TextField(blank=True)
    content = RichTextUploadingField()
    # TODO: Set blank to True when the import is over
    main_image = models.ImageField(blank=True)
    categories = models.ManyToManyField('ArticleCategory')
    creation_time = models.DateTimeField(auto_now_add=True)
    publish_time = models.DateTimeField(blank=True, null=True)
    featured = models.BooleanField(default=False, verbose_name="À la une")

    objects = ArticleManager()
    published = PublishedArticleManager()

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])

    def get_content(self):
        return embed_videos(self.content)

    def get_excerpt(self):
        return truncatewords(
            embed_videos(
                html.unescape(striptags(self.content)),
                strip=True
            ),
            55
        )


class ArticleComment(AbstractComment):
    target = models.ForeignKey(Article, related_name='comments')


class ArticleCategory(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', args=[self.slug])


def get_group_avatar_path(instance, filename):
    root, ext = os.path.splitext(filename)
    return 'avatars_group/{}{}'.format(instance.id, ext)

class DiscussionGroup(models.Model):
    TYPE_NORMAL = 0
    TYPE_GEOGRAPHICAL = 1
    TYPE_FEATURED = 2

    TYPE_CHOICES = [
        (TYPE_NORMAL, "Thématique"),
        (TYPE_GEOGRAPHICAL, "Géographique"),
        (TYPE_FEATURED, "Entraide"),
    ]

    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    description_short = models.TextField(blank=True)
    group_type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_NORMAL)
    private = models.BooleanField(default=False, db_index=True)
    avatar = models.ImageField(
        upload_to=get_group_avatar_path,
        blank=True,
        verbose_name="Avatar"
    )
    display_order = models.SmallIntegerField(default=0, db_index=True)

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

    def title_display(self):
        """Title that includes, if appropriate, the "lock" icon to indicate a private group."""
        if self.private:
            return format_html("{} {}", self.title, fa_str('lock'))
        else:
            return self.title


class DiscussionManager(models.Manager):
    def full_text_search(self, search_query):
        # Postgres full-text index for this search added in migration 0034
        sv = SearchVector('title', 'content', config='french')
        return self.annotate(search=sv)\
            .annotate(rank=SearchRank(sv, search_query))\
            .filter(search=search_query, group__private=False)\
            .order_by('-rank')


class Discussion(CommentableMixin, models.Model):
    group = models.ForeignKey(DiscussionGroup, related_name='discussions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    slug = models.SlugField(max_length=255)
    title = models.CharField(max_length=255, verbose_name="Titre")
    content = RichTextField(config_name='restricted', verbose_name="Message")
    creation_time = models.DateTimeField(auto_now_add=True, db_index=True)
    last_activity = models.DateTimeField(auto_now_add=True, db_index=True)
    last_poster = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    is_locked = models.BooleanField(default=False, db_index=True)
    is_sticky = models.BooleanField(default=False, db_index=True)

    objects = DiscussionManager()

    class Meta:
        unique_together = ('group', 'slug')

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def clean(self):
        self.content = sanitize_comment(self.content)

    def save(self, *args, **kwargs):
        if not self.last_poster and self.author:
            self.last_poster = self.author
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('discussion', args=[self.group.slug, self.slug])

    def update_last_activity(self):
        if self.comments.exists():
            last_comment = self.comments.last()
            self.last_activity = last_comment.submit_date
            self.last_poster = last_comment.user
            self.save()


class DiscussionComment(AbstractComment):
    target = models.ForeignKey(Discussion, related_name='comments')


class ProjectCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


def get_project_image_path(instance, filename, slot):
    root, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext not in ('.jpg', '.jpeg', '.png'):
        ext = '.jpg'
    return 'projects/{}/img{}{}'.format(instance.id, slot, ext)

class ProjectManager(models.Manager):
    def full_text_search(self, search_query):
        # Postgres full-text index for this search added in migration 0033
        sv = SearchVector('title', 'description', 'pattern_name', config='french')
        return self.annotate(search=sv)\
            .annotate(num_likes=Count('likes'))\
            .filter(search=search_query)\
            .order_by('-num_likes')

    def popular_this_week(self):
        last_week = datetime.date.today() - datetime.timedelta(days=7)
        return self.filter(projectvote__date_liked__gt=last_week)\
            .annotate(num_likes=Count('projectvote'))\
            .order_by('-num_likes')


class Project(CommentableMixin, models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='projects')
    title = models.CharField(
        max_length=100,
        verbose_name="Titre du projet",
    )
    description = RichTextField(config_name='restricted')
    category = models.ForeignKey(
        ProjectCategory,
        verbose_name="Catégorie",
    )
    pattern_name = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Patron ou tutoriel utilisé",
    )
    pattern_url = models.URLField(
        max_length=250,
        blank=True,
        verbose_name="URL du patron ou tutoriel",
    )
    blog_post_url = models.URLField(
        max_length=250,
        blank=True,
        verbose_name="Article sur mon blog",
    )
    store_url = models.URLField(
        max_length=250,
        blank=True,
        verbose_name="URL du produit dans votre boutique",
    )
    creation_time = models.DateTimeField(auto_now_add=True)

    # Last time it had the "A la une" button clicked on
    featured_time = models.DateTimeField(null=True)

    # baaah, it's not worth the extra indirection to create a model for project images.
    # Let's go low-tech and have 4 fields.
    image1 = models.ImageField(
        upload_to=partial(get_project_image_path, slot=1),
        verbose_name="Photographie principale du projet",
    )
    image2 = models.ImageField(
        upload_to=partial(get_project_image_path, slot=2),
        blank=True,
        verbose_name="Photographie alternative 1",
    )
    image3 = models.ImageField(
        upload_to=partial(get_project_image_path, slot=3),
        blank=True,
        verbose_name="Photographie alternative 2",
    )
    image4 = models.ImageField(
        upload_to=partial(get_project_image_path, slot=4),
        blank=True,
        verbose_name="Photographie alternative 3",
    )

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_by',
        through='ProjectVote'
    )

    # The old system had a lot of spam users and we chose to aggressively weed them out during the
    # migration. Any user having likes and favorites for its only interactions with the system
    # would not be migrated. To ensure that "like count" would stay the same project-wise, we add
    # this field which corresponds to the number of like the project had from users who haven't
    # been migrated.
    # This field's value never changes and stays to zero for all post-migration projects.
    legacy_like_count = models.PositiveSmallIntegerField(default=0)

    objects = ProjectManager()

    class Meta:
        ordering = ['-creation_time']

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.author, self.title)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        for image_field in self.get_images():
            if not image_field:
                continue
            try:
                with Image.open(image_field.path) as image:
                    w, h = image.size
                    if w > 630 or h > 630:
                        image.thumbnail((630, 630))
                        try:
                            image.save(image_field.path)
                        except OSError:
                            # could be a "cannot write mode P as JPEG" situation.
                            # let's try http://stackoverflow.com/a/21669827
                            try:
                                image.convert('RGB').save(image_field.path)
                            except OSError:
                                # Oh, screw that.
                                image_field.delete()
            except (FileNotFoundError, OSError):
                # Can't read the image, unset it
                image_field.delete()

    def get_absolute_url(self):
        return reverse('project_details', args=[self.id, self.get_slug()])

    def get_slug(self):
        return slugify(self.title)

    def get_images(self):
        return [self.image1, self.image2, self.image3, self.image4]

    def get_like_count(self):
        return self.likes.count() + self.legacy_like_count


class ProjectComment(AbstractComment):
    target = models.ForeignKey(Project, related_name='comments')


class ProjectVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    project = models.ForeignKey(Project)
    date_liked = models.DateTimeField(auto_now_add=True, db_index=True)
    favorite = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('user', 'project')


class PageContents(models.Model):
    key = models.CharField(max_length=30, unique=True)
    contents = RichTextField()

    def __str__(self):
        return self.key

