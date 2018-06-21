from django.core.management.base import BaseCommand

from ...models.article import Article, ArticleComment
from ...models.discussion import DiscussionGroup, Discussion, DiscussionComment
from ...models.page import PageContents
from ...models.project import Project, ProjectComment
from ...models.user import UserProfile

FIELDS = [
    (Article, 'content'),
    (ArticleComment, 'comment'),
    (DiscussionGroup, 'description'),
    (Discussion, 'content'),
    (DiscussionComment, 'comment'),
    (PageContents, 'contents'),
    (Project, 'description'),
    (ProjectComment, 'comment'),
    (UserProfile, 'description'),
]

class Command(BaseCommand):
    help = "Search and replace text in all tn2 text fields"

    def add_arguments(self, parser):
        parser.add_argument(
            'search',
            help="String to search for"
        )
        parser.add_argument(
            'replace',
            help="Replace with this string"
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help="Don't actually replace anything"
        )

    def handle(self, *app_labels, **options):
        search = options['search']
        replace = options['replace']
        for model, fieldname in FIELDS:
            print("Processing {}.{}".format(model.__name__, fieldname))
            for obj in model.objects.all():
                val = getattr(obj, fieldname)
                if search in val:
                    try:
                        identifier = obj.get_absolute_url()
                    except AttributeError:
                        identifier = obj.key
                    print(identifier)
                    if not options['dry_run']:
                        val = val.replace(search, replace)
                        setattr(obj, fieldname, val)
                        obj.save()
        print("Done!")
        if options['dry_run']:
            print('...but not for real, it was a dry run!')
