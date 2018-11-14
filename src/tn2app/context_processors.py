from django.conf import settings

def inject_settings(request):
    return {
        'READONLY': settings.READONLY,
    }


def fromfr(request):
    if request.GET.get('fromfr'):
        return {'FROMFR': True}
    else:
        return {}
