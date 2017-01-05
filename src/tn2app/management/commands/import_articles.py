import html
import os
import os.path
import re
import shutil
from urllib.parse import unquote

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from bs4 import BeautifulSoup

from wordpress.models import WpV2Posts, WpV2Postmeta
from ...models import User, Article

def internalize_links(content, wpcontent_path):
    # These have been verified on the old server: they're broken.
    KNOWN_BROKEN_LINKS = {
        'uploads/2013/02/558722_10151000705976161_417488649_n.jpg',
    }
    soup = BeautifulSoup(content)
    re_tnurl = re.compile(r'http://(www\.)?threadandneedles\.fr/wp-content/(.*)')
    for img in soup.find_all('img'):
        src = img['src']
        m = re_tnurl.match(src)
        if m:
            internalized_url = unquote(m.groups()[1])
            img['src'] = settings.MEDIA_URL + internalized_url
            internalized_path = unquote(internalized_url)
            dest_path = os.path.join(settings.MEDIA_ROOT, internalized_path)
            if not os.path.exists(dest_path.encode('utf-8')):
                src_path = os.path.join(wpcontent_path, internalized_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                try:
                    shutil.copy(src_path.encode('utf-8'), dest_path.encode('utf-8'))
                except FileNotFoundError:
                    if internalized_path not in KNOWN_BROKEN_LINKS:
                        raise Exception("Warning: couldn't find {}".format(src_path))

    return str(soup)


class Command(BaseCommand):
    help = 'Imports articles from our WP DB'

    def add_arguments(self, parser):
        parser.add_argument(
            'wpcontent_path',
            help="Path where wp-content is"
        )

    def handle(self, *args, **options):
        wpcontent_path = options['wpcontent_path']
        uploads_path = os.path.join(wpcontent_path, 'uploads')
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
                    'title': html.unescape(wppost.post_title),
                    'content': internalize_links(wppost.post_content, wpcontent_path),
                    'creation_time': wppost.post_modified,
                    'publish_time': wppost.post_date if status == Article.STATUS_PUBLISHED else None,
                }
            )
            if created and attachment_relpath:
                with open(os.path.join(uploads_path, attachment_relpath), 'rb') as fp:
                    dfile = File(fp)
                    article.main_image.save(attachment_relpath, dfile)

