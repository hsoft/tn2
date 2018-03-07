import os.path

from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db import models
from django.db.models import Max
from django.urls import reverse
from django.utils.html import format_html

from ckeditor.fields import RichTextField

from ..util import nonone, fa_str, sanitize_comment
from .comment import CommentableMixin, AbstractComment


__all__ = ['DiscussionGroup', 'Discussion', 'DiscussionComment', 'get_group_avatar_path']

def get_group_avatar_path(instance, filename):
    root, ext = os.path.splitext(filename)
    return 'avatars_group/{}{}'.format(instance.id, ext)

class DiscussionGroup(models.Model):
    class Meta:
        permissions = (
            ('access_private_groups', "Accéder aux groupes privés"),
        )
        app_label = 'tn2app'

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
    group_type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_NORMAL, db_index=True)
    private = models.BooleanField(default=False, db_index=True)
    restrict_access_to = models.ForeignKey(
        'auth.Group',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    avatar = models.ImageField(
        upload_to=get_group_avatar_path,
        blank=True,
        verbose_name="Avatar"
    )
    display_order = models.SmallIntegerField(default=0, db_index=True)
    # flag for the group "Brocante", a group where topics are ephemeral and
    # where we want to relax rules about topic deletion.
    ephemeral_topics = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.slug, self.title)

    def get_absolute_url(self):
        return reverse('discussion_group', args=[self.slug])

    def can_be_seen_by_user(self, user):
        if not self.private:
            return True
        if not user.has_perm('tn2app.access_private_groups'):
            return False
        return self.restrict_access_to in user.groups.all()

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
            .order_by('-rank', '-id')


class Discussion(CommentableMixin, models.Model):
    class Meta:
        unique_together = ('group', 'slug')
        app_label = 'tn2app'

    group = models.ForeignKey(
        DiscussionGroup,
        related_name='discussions',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='+',
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(max_length=255, db_index=True)
    title = models.CharField(max_length=255, verbose_name="Titre")
    content = RichTextField(config_name='restricted', verbose_name="Message")
    creation_time = models.DateTimeField(auto_now_add=True, db_index=True)
    last_activity = models.DateTimeField(auto_now_add=True, db_index=True)
    last_poster = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    is_locked = models.BooleanField(default=False, db_index=True)
    is_sticky = models.BooleanField(default=False, db_index=True)

    objects = DiscussionManager()

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

    def can_delete(self):
        return self.group.ephemeral_topics or not self.comments.exists()

    def update_last_activity(self):
        if self.comments.exists():
            last_comment = self.comments.last()
            self.last_activity = last_comment.submit_date
            self.last_poster = last_comment.user
            self.save()


class DiscussionComment(AbstractComment):
    target = models.ForeignKey(
        Discussion,
        related_name='comments',
        on_delete=models.CASCADE,
    )

    def get_absolute_url(self):
        prior_comments_count = self.target.comments.filter(id__lt=self.id).count()
        pageno = (prior_comments_count // settings.DISCUSSION_PAGINATE_BY) + 1
        return self.target.get_absolute_url() + '?page={}#c{}'.format(pageno, self.id)

