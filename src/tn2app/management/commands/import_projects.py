import html
import os.path
import re
from unicodedata import normalize

from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.html import strip_tags, linebreaks

from wordpress.models import (
    WpV2BpCoutureProjets, WpV2BpCoutureImages, WpV2BpCoutureCategories, WpV2Users
)
from ...models import Project, ProjectCategory, User
from ...util import unescape_mysql

def s(val):
    return unescape_mysql(strip_tags(html.unescape(val)))

class Command(BaseCommand):
    help = 'Imports projects from our WP DB'

    def add_arguments(self, parser):
        parser.add_argument(
            'wpcontent_path',
            help="Path where wp-content is"
        )
        parser.add_argument(
            '--project-id',
            default=0,
            type=int,
            help="Specify a single project ID to import"
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

        re_link = re.compile(r'<a href="(.*?)".*>(.*)</a>')
        if options['project_id']:
            wpprojs = [WpV2BpCoutureProjets.objects.get(id=options['project_id'])]
        else:
            wpprojs = WpV2BpCoutureProjets.objects.order_by('-id')
        for wpproj in wpprojs:
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
                pattern_url, pattern_name = m.groups()
            else:
                pattern_name = wpproj.patron
                pattern_url = ''
            proj, created = Project.objects.get_or_create(
                id=wpproj.id,
                defaults={
                    'author': author,
                    'title': s(wpproj.title),
                    'description': linebreaks(s(wpproj.description)),
                    'category_id': catid,
                    'pattern_name': s(pattern_name),
                    'pattern_url': s(pattern_url),
                    'blog_post_url': s(wpproj.url),
                    'store_url': s(wpproj.market_id),
                }
            )
            # If targeting a single project, we always re-import photos
            if created or options['project_id']:
                print("Created project {}".format(proj))
                proj.creation_time = wpproj.date_created
                proj.save()
                wpimages = WpV2BpCoutureImages.objects.filter(project_id=proj.id).order_by('-is_main_picture')
                counter = 1
                for wpimage in wpimages[:4]:
                    # in the DB, our path start with /var/www/threadandneedles.fr/wp-content and we
                    # want to get rid of that.
                    src_relpath = '/'.join(wpimage.img_large_dir.split('/')[5:])
                    src_path = '/'.join([wpcontent_path, src_relpath])
                    if not os.path.exists(src_path):
                        src_path = normalize('NFC', src_path)
                        if not os.path.exists(src_path):
                            print("Can't find file {}, skipping".format(repr(src_path)))
                            continue
                    with open(src_path, 'rb') as fp:
                        dfile = File(fp)
                        image_field = getattr(proj, 'image{}'.format(counter))
                        image_field.save(src_relpath, dfile)
                        counter += 1
                if counter == 1:
                    print("No image! deleting project")
                    proj.delete()

