import datetime

from django.core.management.base import BaseCommand

from ...models import Message

class Command(BaseCommand):
    help = "Delete old messages"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help="Don't actually delete anything"
        )

    def handle(self, *app_labels, **options):
        MESSAGE_LIFETIME_IN_DAYS = 30
        time_limit = datetime.datetime.now() - datetime.timedelta(days=MESSAGE_LIFETIME_IN_DAYS)
        old_messages = Message.objects.filter(creation_time__lt=time_limit)

        print("Deleting {} messages...".format(old_messages.count()))
        if options['dry_run']:
            print("Just kidding! this was a dry run.")
        else:
            old_messages.delete()
            print("Done!")
