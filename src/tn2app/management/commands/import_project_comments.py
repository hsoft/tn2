from django.core.management.base import BaseCommand
from django.utils.html import linebreaks

from django_comments.models import Comment

from wordpress.models import (
    WpV2BpCoutureCommentaires, WpV2Users
)
from tn2comments.util import sanitize_comment
from ...models import Project, User
from ...util import unescape_mysql

class Command(BaseCommand):
    help = 'Imports project comments from our WP DB'

    def handle(self, *args, **options):
        for proj in Project.objects.all():
            Comment.objects.for_model(proj).delete()
            wpcomments = WpV2BpCoutureCommentaires.objects.filter(item_id=proj.id)
            for wpcomment in wpcomments.all():
                try:
                    author = User.objects.get_from_wpuser_id(wpcomment.user_id)
                except WpV2Users.DoesNotExist:
                    print("WP user id {} doesn't exist? strange...".format(wpcomment.user_id))
                    continue
                Comment.objects.create(
                    content_object=proj,
                    site_id=1,
                    user=author,
                    comment=linebreaks(unescape_mysql(sanitize_comment(wpcomment.content))),
                    submit_date=wpcomment.date_posted,
                )

