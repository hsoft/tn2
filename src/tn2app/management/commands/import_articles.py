import os.path

from django.core.files import File
from django.core.management.base import BaseCommand

from wordpress.models import WpV2Posts, WpV2Postmeta
from ...models import User, Article

class Command(BaseCommand):
    help = 'Imports articles from our WP DB'

    def add_arguments(self, parser):
        parser.add_argument(
            'uploads_path',
            help="Path where WP uploads are"
        )

    def handle(self, *args, **options):
        uploads_path = options['uploads_path']
        wpposts = WpV2Posts.objects\
            .filter(post_type='post', post_status__in={'draft', 'pending', 'publish'})
        for wppost in wpposts.all():
            print(wppost.post_name, wppost.post_status)
            try:
                thumbnail_id = WpV2Postmeta.objects.get(post_id=wppost.id, meta_key='_thumbnail_id').meta_value
                attachment_relpath = WpV2Postmeta.objects.get(post_id=thumbnail_id, meta_key='_wp_attached_file').meta_value
                print(attachment_relpath)

            except WpV2Postmeta.DoesNotExist:
                attachment_relpath = None
            author = User.objects.get_from_wpuser_id(wppost.post_author)
            print(author)
            status = {
                'draft': Article.STATUS_DRAFT,
                'pending': Article.STATUS_REVISION,
                'publish': Article.STATUS_PUBLISHED,
            }[wppost.post_status]
            slug = "{}-{}".format(wppost.id, wppost.post_name)
            article, created = Article.objects.get_or_create(
                slug=slug,
                defaults={
                    'author': author,
                    'status': status,
                    'title': wppost.post_title,
                    'content': wppost.post_content,
                    'creation_time': wppost.post_modified,
                    'publish_time': wppost.post_date if status == Article.STATUS_PUBLISHED else None,
                }
            )
            if created and attachment_relpath:
                with open(os.path.join(uploads_path, attachment_relpath), 'rb') as fp:
                    dfile = File(fp)
                    article.main_image.save(attachment_relpath, dfile)

