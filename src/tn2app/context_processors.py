from django.conf import settings

def inject_settings(request):
    return {
        'READONLY': settings.READONLY,
    }
