import html

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from wordpress.models import WpV2Users, WpV2BpXprofileData

class Command(BaseCommand):
    help = 'Imports buddypress profiles into users with a wpdb_id'

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.filter(profile__wpdb_id__isnull=False)
        print("Processing {} users".format(users.count()))

        for user in users.all():
            print("{} ({})".format(user.username, user.profile.wpdb_id))
            wpuser = WpV2Users.objects.get(id=user.profile.wpdb_id)
            bp_fields = wpuser.bp_profile_fields
            FIELD2WPID = [
                ('display_name', 1),
                ('description', 54),
                ('city', 3),
                ('website', 2),
                ('skill_level', 5),
                ('sewing_machine', 11),
            ]
            for fieldname, wpid in FIELD2WPID:
                try:
                    value = bp_fields.get(field_id=wpid).value
                except WpV2BpXprofileData.DoesNotExist:
                    continue
                except WpV2BpXprofileData.MultipleObjectsReturned:
                    print("Multiple field objects (field_id={})? Now that's strange...".format(wpid))
                    value = bp_fields.filter(field_id=wpid).first().value
                value = html.unescape(value).replace('\\\'', '\'')
                setattr(user.profile, fieldname, value)
            if len(user.profile.website) > 200:
                print("Something's wrong with this URL: {}".format(user.profile.website))
                user.profile.website = ''
            user.profile.save()
