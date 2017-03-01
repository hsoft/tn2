from django.core.management.base import BaseCommand
from django.utils.html import linebreaks

from wordpress.models import WpV2Comments, WpV2Users
from ...models import User, Article
from ...util import sanitize_comment

class Command(BaseCommand):
    help = 'Imports articles\' comments from our WP DB'

    def handle(self, *args, **options):
        for article in Article.objects.all():
            slug = article.slug
            wpid = slug.split('-')[0]
            if not wpid.isdigit():
                # Not originating from wp
                continue
            # Those comments are causing problems, let's just skip them...
            BLACKLIST = {17505}
            wpcomments = WpV2Comments.objects\
                .filter(comment_post_id=wpid, comment_approved='1', comment_type='')\
                .exclude(user_id=0)\
                .exclude(comment_id__in=BLACKLIST)
            article.comments.all().delete()
            if not wpcomments.exists():
                continue
            print("Adding {} comments to article {}".format(wpcomments.count(), article.slug))
            for wpcomment in wpcomments.all():
                try:
                    author = User.objects.get_from_wpuser_id(wpcomment.user_id)
                except WpV2Users.DoesNotExist:
                    print("WP user id {} doesn't exist? strange...".format(wpcomment.user_id))
                    continue
                comment = article.comments.create(
                    user=author,
                    comment=linebreaks(sanitize_comment(wpcomment.comment_content)),
                )
                # auto_now_add can't be overriden during create().
                comment.submit_date = wpcomment.comment_date
                comment.save()

