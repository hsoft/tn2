from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
import django.views.static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('tn2app.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', django.views.static.serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
