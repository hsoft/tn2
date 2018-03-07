import datetime
import html

from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import striptags, truncatewords
from django.urls import reverse

from ckeditor_uploader.fields import RichTextUploadingField

from ..util import embed_videos
from .comment import CommentableMixin, AbstractComment


__all__ = ['Article', 'ArticleCategory', 'ArticleComment']

class ArticleManager(models.Manager):
    def filter_by_published(self, qs):
        return qs.filter(
            status=Article.STATUS_PUBLISHED,
            publish_time__lt=datetime.datetime.now(),
        )

    def full_text_search(self, search_query):
        # Postgres full-text index for this search added in migration 0031
        sv = SearchVector('title', 'content', config='french')
        qs = self.annotate(search=sv).annotate(rank=SearchRank(sv, search_query))
        qs = self.filter_by_published(qs)
        qs = qs.filter(search=search_query)
        return qs.order_by('-rank', '-id')


class PublishedArticleManager(ArticleManager):
    def get_queryset(self):
        return self.filter_by_published(super().get_queryset())


class Article(CommentableMixin, models.Model):
    class Meta:
        app_label = 'tn2app'

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
        on_delete=models.PROTECT,
    )
    slug = models.SlugField(max_length=255, unique=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True)
    content = RichTextUploadingField()
    main_image = models.ImageField(upload_to='articles', blank=True)
    categories = models.ManyToManyField('ArticleCategory')
    creation_time = models.DateTimeField(auto_now_add=True, db_index=True)
    publish_time = models.DateTimeField(blank=True, null=True, db_index=True)
    featured = models.BooleanField(default=False, verbose_name="À la une", db_index=True)

    objects = ArticleManager()
    published = PublishedArticleManager()

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def is_published(self):
        return self.status == self.STATUS_PUBLISHED and self.publish_time < datetime.datetime.now()

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
    target = models.ForeignKey(
        Article,
        related_name='comments',
        on_delete=models.CASCADE,
    )


class ArticleCategory(models.Model):
    class Meta:
        app_label = 'tn2app'

    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', args=[self.slug])



