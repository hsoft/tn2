import html
import re

from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.html import strip_tags

from wordpress.models import (
    WpV2BpCoutureProjets, WpV2BpCoutureImages, WpV2BpCoutureCategories, WpV2Users
)
from ...models import Project, ProjectCategory, User

def s(val):
    return strip_tags(html.unescape(val))

class Command(BaseCommand):
    help = 'Imports article categories from our WP DB'

    def add_arguments(self, parser):
        parser.add_argument(
            'wpcontent_path',
            help="Path where wp-content is"
        )

    def handle(self, *args, **options):
        wpcontent_path = options['wpcontent_path']
        for wpcat in WpV2BpCoutureCategories.objects.all():
            cat, created = ProjectCategory.objects.get_or_create(
                id=wpcat.id,
                defaults={
                    'name': s(wpcat.title),
                    'description': s(wpcat.description),
                }
            )
            if created:
                print("Create category {}".format(cat))

        re_link = re.compile(r'<a href="(.*)">(.*)</a>')
        for wpproj in WpV2BpCoutureProjets.objects.order_by('-id'):
            try:
                author = User.objects.get_from_wpuser_id(wpproj.user_id)
            except WpV2Users.DoesNotExist:
                print("WP user id {} doesn't exist? strange...".format(wpproj.user_id))
                continue
            catid = wpproj.categorie
            if catid == 0:
                # Only one project, and it's a bag, and bag cat id is 8
                catid = 8
            m = re_link.match(wpproj.patron)
            if m:
                pattern_name, pattern_url = m.groups()
            else:
                pattern_name = wpproj.patron
                pattern_url = ''
            proj, created = Project.objects.get_or_create(
                id=wpproj.id,
                defaults={
                    'author': author,
                    'title': s(wpproj.title),
                    'description': s(wpproj.description),
                    'category_id': catid,
                    'pattern_name': s(pattern_name),
                    'pattern_url': s(pattern_url),
                    'blog_post_url': s(wpproj.url),
                    'store_url': s(wpproj.market_id),
                }
            )
            if created:
                print("Created project {}".format(proj))
                proj.creation_time = wpproj.date_created
                proj.save()
                wpimages = WpV2BpCoutureImages.objects.filter(project_id=proj.id).order_by('-is_main_picture')
                for index, wpimage in enumerate(wpimages[:4], start=1):
                    # in the DB, our path start with /var/www/threadandneedles.fr/wp-content and we
                    # want to get rid of that.
                    src_relpath = '/'.join(wpimage.img_large_dir.split('/')[5:])
                    src_path = '/'.join([wpcontent_path, src_relpath])
                    try:
                        with open(src_path, 'rb') as fp:
                            dfile = File(fp)
                            image_field = getattr(proj, 'image{}'.format(index))
                            image_field.save(src_relpath, dfile)
                    except FileNotFoundError:
                        print("Can't find file {}, skipping".format(repr(src_path)))

