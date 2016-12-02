from django.apps import AppConfig


class Tn2AppConfig(AppConfig):
    name = 'tn2app'

    def ready(self):
        from django_comments.signals import comment_will_be_posted, comment_was_posted
        from . import signals
        comment_will_be_posted.connect(signals.comment_will_be_posted)
        comment_was_posted.connect(signals.comment_was_posted)
