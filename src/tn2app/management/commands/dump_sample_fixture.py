import shutil
import os
from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand

from ...models import Article, Project, DiscussionGroup
from ...util import extract_media_paths

class Command(BaseCommand):
    def handle(self, *app_labels, **options):
        fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fixtures'))

        def copy_media(media_path):
            if not media_path:
                return
            srcpath = os.path.join(settings.MEDIA_ROOT, media_path)
            destpath = os.path.join(fixture_dir, 'media', media_path)
            os.makedirs(os.path.dirname(destpath), exist_ok=True)
            shutil.copy(srcpath, destpath)

        def get_objects():
            articles = Article.published.all().order_by('-id')[:10]
            projects = Project.objects.all().order_by('-id')[:20]
            groups = DiscussionGroup.objects.filter(private=False).all()
            yielded_users = set()

            def yield_user(u):
                if u not in yielded_users:
                    # anonymize. We don't save because we don't actually want to!
                    u.set_unusable_password()
                    u.email = '{}@example.com'.format(u.username)
                    yield u
                    if u.profile:
                        yield u.profile
                    yielded_users.add(u)
                    copy_media(u.profile.avatar.name)

            for article in articles:
                yield from yield_user(article.author)
                yield article
                copy_media(article.main_image.name)
                for media_path in extract_media_paths(article.content):
                    copy_media(media_path)

            for project in projects:
                yield from yield_user(project.author)
                yield project
                for img in project.get_images():
                    copy_media(img.name)

            for group in groups:
                if group.group_type == DiscussionGroup.TYPE_FEATURED:
                    for discussion in group.discussions.all().order_by('-last_activity')[:20]:
                        yield from yield_user(discussion.author)
                        yield discussion

                        for comment in discussion.comments.all():
                            yield from yield_user(comment.user)
                            yield comment

                yield group
                copy_media(group.avatar.name)

        serializers.serialize(
            'json', get_objects(),
            stream=self.stdout,
        )

