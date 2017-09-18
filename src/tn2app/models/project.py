import datetime
import os.path
from functools import partial

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.text import slugify

from ckeditor.fields import RichTextField

from ..util import PermissiveURLField
from .comment import CommentableMixin, AbstractComment
from .pattern import Pattern, PatternCategory


__all__ = ['Contest', 'Project', 'ProjectComment', 'ProjectVote', 'get_project_image_path']

class ContestManager(models.Manager):
    def active_contest(self):
        return self.filter(active=True).last()


class Contest(models.Model):
    class Meta:
        verbose_name = "Concours"
        verbose_name_plural = "Concours"

    name = models.TextField(verbose_name="Nom")
    active = models.BooleanField(default=False, db_index=True, verbose_name="Actif")

    objects = ContestManager()

    def __str__(self):
        return self.name


def get_project_image_path(instance, filename, slot):
    root, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext not in ('.jpg', '.jpeg', '.png'):
        ext = '.jpg'
    return 'user/{}/project/{}/img{}{}'.format(instance.author.id, instance.id, slot, ext)

class ProjectManager(models.Manager):
    def full_text_search(self, search_query):
        # Postgres full-text index for this search added in migration 0033
        sv = SearchVector('title', 'description', 'pattern_name', config='french')
        # There's a weird situation here where our naive query ends up with a stray "GROUP BY"
        # clause which makes our whole query go very slow. I haven't figured out why yet. However,
        # proceeding through subqueries like we do here does the trick, so that's what we'll do.
        subq = self.annotate(search=sv)\
            .filter(search=search_query)
        return self.filter(id__in=subq)\
            .annotate(num_likes=Count('likes'))\
            .order_by('-num_likes', '-id')

    def popular_this_week(self, count=3):
        # This code below to get projects ordered by a num_likes might seem needlessly complicated, but
        # it's an optimisation! The naive query, a Project annotate() of Count('likes') is very slow
        # because (I think) of the join. Directly counting on ProjectVote without joining cuts time
        # in half.
        last_week = datetime.date.today() - datetime.timedelta(days=7)
        popular_projects_values = ProjectVote.objects.filter(date_liked__gt=last_week)\
            .values('project')\
            .annotate(num_likes=Count('*'))\
            .order_by('-num_likes').all()[:count]
        popular_projects_ids = [d['project'] for d in popular_projects_values]
        popular_projects_bulk = Project.objects.in_bulk(popular_projects_ids)
        return [popular_projects_bulk[pid] for pid in popular_projects_ids]


class Project(CommentableMixin, models.Model):
    class Meta:
        ordering = ['-creation_time']
        app_label = 'tn2app'

    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='projects')
    title = models.CharField(
        max_length=100,
        verbose_name="Titre du projet",
    )
    description = RichTextField(config_name='restricted')
    target = models.PositiveSmallIntegerField(
        db_index=True,
        choices=Pattern.TARGET_CHOICES,
        null=True,
        verbose_name="Destinataire",
    )
    domain = models.PositiveSmallIntegerField(
        db_index=True,
        choices=Pattern.DOMAIN_CHOICES,
        null=True,
        verbose_name="Domaine",
    )
    category = models.ForeignKey(
        PatternCategory,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="Catégorie",
    )
    pattern = models.ForeignKey(
        Pattern,
        null=True,
        blank=True,
        verbose_name="Patron",
    )
    pattern_name = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Patron ou tutoriel utilisé",
    )
    pattern_url = PermissiveURLField(
        max_length=250,
        blank=True,
        verbose_name="URL du patron ou tutoriel",
    )
    blog_post_url = PermissiveURLField(
        max_length=250,
        blank=True,
        verbose_name="Article sur mon blog",
    )
    store_url = PermissiveURLField(
        max_length=250,
        blank=True,
        verbose_name="URL du produit dans votre boutique",
    )
    creation_time = models.DateTimeField(auto_now_add=True, db_index=True)

    # Last time it had the "A la une" button clicked on
    featured_time = models.DateTimeField(null=True, db_index=True)

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
        related_name='liked_projects',
        through='ProjectVote'
    )

    contest = models.ForeignKey(
        Contest,
        related_name='projects',
        null=True,
        blank=True,
    )

    # The old system had a lot of spam users and we chose to aggressively weed them out during the
    # migration. Any user having likes and favorites for its only interactions with the system
    # would not be migrated. To ensure that "like count" would stay the same project-wise, we add
    # this field which corresponds to the number of like the project had from users who haven't
    # been migrated.
    # This field's value never changes and stays to zero for all post-migration projects.
    legacy_like_count = models.PositiveSmallIntegerField(default=0)

    objects = ProjectManager()

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.author, self.title)

    def save(self, *args, **kwargs):
        # http://stackoverflow.com/a/15776267
        if self.pk is None:
            saved_images = [self.image1, self.image2, self.image3, self.image4]
            self.image1 = self.image2 = self.image3 = self.image4 = None
            super().save(*args, **kwargs)
            self.image1, self.image2, self.image3, self.image4 = saved_images

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project_details', args=[self.id, self.get_slug()])

    def get_slug(self):
        return slugify(self.title)

    def get_images(self):
        result = [self.image1, self.image2, self.image3, self.image4]
        return [i for i in result if i]

    def get_like_count(self):
        return self.likes.count() + self.legacy_like_count


class ProjectComment(AbstractComment):
    target = models.ForeignKey(Project, related_name='comments')


class ProjectVote(models.Model):
    class Meta:
        unique_together = ('user', 'project')
        app_label = 'tn2app'

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    project = models.ForeignKey(Project)
    date_liked = models.DateTimeField(auto_now_add=True, db_index=True)
    favorite = models.BooleanField(default=False, db_index=True)
