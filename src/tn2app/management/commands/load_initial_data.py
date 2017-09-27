from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models.signals import post_save

from ...models import DiscussionComment, Project

class Command(BaseCommand):
    def handle(self, *app_labels, **options):
        if Project.objects.exists():
            print("We already have data. Skip load_initial_data.")
            return
        assert post_save.disconnect(sender=DiscussionComment, dispatch_uid='discussioncomment_was_saved')
        FIXTURES = [
            'pages',
            'emails',
            'articlecategory',
            'patterncategory',
            'sample_data',
        ]
        for fixture in FIXTURES:
            call_command('loaddata', fixture, app_label='tn2app')

