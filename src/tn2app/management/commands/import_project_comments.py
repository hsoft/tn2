from django.core.management.base import BaseCommand
from django.utils.html import linebreaks

from wordpress.models import (
    WpV2BpCoutureCommentaires, WpV2Users
)
from ...models import Project, User
from ...util import unescape_mysql, sanitize_comment

class Command(BaseCommand):
    help = 'Imports project comments from our WP DB'

    def handle(self, *args, **options):
        for proj in Project.objects.all():
            proj.comments.all().delete()
            wpcomments = WpV2BpCoutureCommentaires.objects.filter(item_id=proj.id)
            for wpcomment in wpcomments.all():
                try:
                    author = User.objects.get_from_wpuser_id(wpcomment.user_id)
                except WpV2Users.DoesNotExist:
                    print("WP user id {} doesn't exist? strange...".format(wpcomment.user_id))
                    continue
                comment = proj.comments.create(
                    user=author,
                    comment=linebreaks(unescape_mysql(sanitize_comment(wpcomment.content))),
                )
                # auto_now_add can't be overriden during create().
                comment.submit_date = wpcomment.date_posted
                comment.save()

