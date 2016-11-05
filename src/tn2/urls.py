from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
import django.views.static
from django.contrib.auth import views as auth_views

from account import views as account_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^account/login/$', account_views.LoginView.as_view(), name='account_login'),
    url(r'^account/logout/$', auth_views.logout, name='account_logout'),
    url(r'^account/password/reset/$', account_views.PasswordResetView.as_view(), name='account_password_reset'),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^', include('tn2app.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', django.views.static.serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
