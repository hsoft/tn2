from django.core import serializers
from django.core.management.base import BaseCommand

from ...models import DiscussionGroup

class Command(BaseCommand):
    help = "Dump specified discussion groups along with all FK models (recursively)."

    def add_arguments(self, parser):
        parser.add_argument(
            'pks', nargs='+',
            help="PKs of groups to dump"
        )

    def handle(self, *app_labels, **options):
        pks = options['pks']

        def get_objects():
            groups = DiscussionGroup.objects.filter(pk__in=pks)
            yielded_users = set()

            def yield_user(u):
                if u not in yielded_users:
                    yield u
                    if u.profile:
                        yield u.profile
                    yielded_users.add(u)

            for group in groups:
                for discussion in group.discussions.all():
                    yield from yield_user(discussion.author)
                    yield discussion

                    for comment in discussion.comments.all():
                        yield from yield_user(comment.user)
                        yield comment

                yield group

        serializers.serialize(
            'json', get_objects(),
            stream=self.stdout,
        )
