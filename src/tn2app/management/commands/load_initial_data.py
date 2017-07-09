import shutil
import os
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models.signals import post_save

from ...models import DiscussionComment

class Command(BaseCommand):
    def handle(self, *app_labels, **options):
        assert post_save.disconnect(sender=DiscussionComment, dispatch_uid='discussioncomment_was_saved')
        FIXTURES = [
            'pages',
            'emails',
            'articlecategory',
            'projectcategory',
            'patterncategory',
            'sample_data',
        ]
        for fixture in FIXTURES:
            call_command('loaddata', fixture, app_label='tn2app')
        fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fixtures'))
        srcpath = os.path.join(fixture_dir, 'media')
        destpath = settings.MEDIA_ROOT
        if os.path.exists(destpath):
            shutil.rmtree(destpath)
        shutil.copytree(srcpath, destpath)

