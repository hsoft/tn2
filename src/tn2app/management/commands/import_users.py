from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import get_hasher
from django.db.utils import IntegrityError

from ...models import UserProfile
from wordpress.models import (
    WpV2Users, WpV2BpCoutureCommentaires, WpV2BpCoutureFavoris, WpV2BpCoutureProjets,
    WpV2BpCoutureVotes, WpV2BpGroupsMembers, WpV2Comments,
)

class Command(BaseCommand):
    help = 'Imports active users from our WP DB'

    def handle(self, *args, **options):
        # Some abusive accounts I've noticed. Certainly only a small part of them, but still, let's
        # not improt them.
        BLACKLIST = {
            40394,
        }
        User = get_user_model()
        hasher = get_hasher('phpass')
        wpusers = WpV2Users.objects.filter(user_status=0).exclude(id__in=BLACKLIST).all()
        print("Processing {} users".format(wpusers.count()))

        for wpuser in wpusers.all():
            if User.objects.filter(profile__wpdb_id=wpuser.id).exists():
                # already imported
                continue
            # Before we import our user, we'll verify that we have something, *anything* linked
            # to that user (a project, a like/favorite, a forum comment). If not, we don't bother
            # importing a ghost user.
            MODELS = [
                WpV2BpCoutureCommentaires, WpV2BpCoutureFavoris, WpV2BpCoutureProjets,
                WpV2BpCoutureVotes, WpV2BpGroupsMembers, WpV2Comments,
            ]
            for model in MODELS:
                if model.objects.filter(user_id=wpuser.id).exists():
                    break
            else:
                print("User {} never did anything. Skipping.".format(wpuser.user_login))
                continue
            print("{} ({})".format(wpuser.user_login, wpuser.id))
            try:
                user = User.objects.create(
                    username=wpuser.user_login,
                    email=wpuser.user_email,
                    password=hasher.from_orig(wpuser.user_pass),
                    is_active=True,
                )
            except IntegrityError:
                print("Already exists!")
                continue
            UserProfile.objects.create(user=user, wpdb_id=wpuser.id)
