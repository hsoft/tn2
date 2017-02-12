import html

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from account.models import EmailAddress

from wordpress.models import WpV2Users, WpV2Usermeta, WpV2BpXprofileData
from ...util import unescape_mysql

class Command(BaseCommand):
    help = 'Imports buddypress profiles into users with a wpdb_id'

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.filter(profile__wpdb_id__isnull=False)
        print("Processing {} users".format(users.count()))

        for user in users.all():
            print("{} ({})".format(user.username, user.profile.wpdb_id))
            # First, let's make sure that we have a django-user-account email model associated with
            # this user.

            # these users below have duplicate email addresses in the old system. We've got to pick
            # one. In each of the case, a manual review of the accounts was made and a user was
            # picked. Email-less users can't log in.
            EMAILLESS_USERS = {
                'watoowatoo',
                'essamra',
                'curlingfox',
            }
            if user.username not in EMAILLESS_USERS and not EmailAddress.objects.get_primary(user):
                EmailAddress.objects.create(
                    user=user,
                    email=user.email,
                    verified=True,
                    primary=True,
                )

            # Now, the WP profile
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
                value = unescape_mysql(html.unescape(value))
                setattr(user.profile, fieldname, value)
            if len(user.profile.website) > 200:
                print("Something's wrong with this URL: {}".format(user.profile.website))
                user.profile.website = ''

            wpdescription = WpV2Usermeta.objects.filter(user_id=wpuser.id, meta_key='description').last()
            if wpdescription:
                user.profile.description_for_articles = unescape_mysql(html.unescape(wpdescription.meta_value))

            user.profile.save()
