import os
import os.path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Imports avatars from each WP user into tn2'

    def add_arguments(self, parser):
        parser.add_argument(
            'avatars_path',
            help="Path where WP avatars are (uploads/avatars)"
        )

    def handle(self, *args, **options):
        avatars_path = options['avatars_path']
        User = get_user_model()
        users = User.objects.filter(profile__wpdb_id__isnull=False)
        print("Processing {} users".format(users.count()))

        for user in users.all():
            user_path = os.path.join(avatars_path, str(user.profile.wpdb_id))
            if not os.path.exists(user_path):
                continue
            possible_matches = [fn for fn in os.listdir(user_path) if os.path.splitext(fn)[0].endswith('bpfull')]
            if possible_matches:
                print("{} ({})".format(user.username, user.profile.wpdb_id))
                # You think that's stupid? damn right! but that's the *actual* logic from buddypress.
                to_import = possible_matches[-1]
                print("Importing {}".format(to_import))
                with open(os.path.join(user_path, to_import), 'rb') as fp:
                    dfile = File(fp)
                    user.profile.avatar.save(to_import, dfile)

