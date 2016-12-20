from django.core.management.base import BaseCommand

from wordpress.models import (
    WpV2BpCoutureVotes
)
from ...models import Project, ProjectVote, User

class Command(BaseCommand):
    help = 'Imports project likes from our WP DB'

    def handle(self, *args, **options):
        for proj in Project.objects.all():
            ProjectVote.objects.filter(project=proj).delete()
            wpvotes = WpV2BpCoutureVotes.objects.filter(project_id=proj.id)
            legacy_vote_count = 0
            votes = []
            wpuserids = {wpvote.user_id for wpvote in wpvotes.all()}
            for wpuserid in wpuserids:
                try:
                    user = User.objects.get(profile__wpdb_id=wpuserid)
                except User.DoesNotExist:
                    legacy_vote_count += 1
                    continue

                votes.append(ProjectVote(user=user, project=proj))

            print("Creating {} likes ({} legacy) for project {}".format(len(votes), legacy_vote_count, proj))
            ProjectVote.objects.bulk_create(votes)
            proj.legacy_like_count = legacy_vote_count
            proj.save()