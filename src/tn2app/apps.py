from django.apps import AppConfig


class Tn2AppConfig(AppConfig):
    name = 'tn2app'

    def ready(self):
        from . import signals # noqa
