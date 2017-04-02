import datetime

from django.core.management.base import BaseCommand

from ...models import Notification

class Command(BaseCommand):
    help = "Delete old notifications"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help="Don't actually delete anything"
        )

    def handle(self, *app_labels, **options):
        NOTIF_LIFETIME_IN_DAYS = 5
        time_limit = datetime.datetime.now() - datetime.timedelta(days=NOTIF_LIFETIME_IN_DAYS)
        old_notifs = Notification.objects.filter(time__lt=time_limit)

        print("Deleting {} notifications...".format(old_notifs.count()))
        if options['dry_run']:
            print("Just kidding! this was a dry run.")
        else:
            old_notifs.delete()
            print("Done!")
