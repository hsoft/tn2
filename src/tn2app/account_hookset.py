from account.conf import settings
from account.hooks import AccountDefaultHookSet
from post_office import mail

class AccountHookset(AccountDefaultHookSet):
    def send_confirmation_email(self, to, ctx):
        mail.send(
            to,
            settings.DEFAULT_FROM_EMAIL,
            template='confirmation_email',
            context=ctx,
        )

    def send_password_reset_email(self, to, ctx):
        mail.send(
            to,
            settings.DEFAULT_FROM_EMAIL,
            template='password_reset_email',
            context=ctx,
        )

    def send_password_change_email(self, to, ctx):
        mail.send(
            to,
            settings.DEFAULT_FROM_EMAIL,
            template='password_change',
            context=ctx,
        )
