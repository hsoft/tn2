from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
import django.views.static
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test

from account import views as account_views
from ckeditor_uploader import views as ckeditor_views
from tn2app import views as tn2_views

ckperms = user_passes_test(lambda user: user.has_perm('tn2app.add_article'))

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^account/signup/$', tn2_views.SignupView.as_view(), name='account_signup'),
    url(r'^account/confirm_email/(?P<key>\w+)/$', account_views.ConfirmEmailView.as_view(), name='account_confirm_email'),
    url(r'^account/login/$', account_views.LoginView.as_view(), name='account_login'),
    url(r'^account/logout/$', auth_views.logout, name='account_logout'),
    url(r'^account/password/reset/$', account_views.PasswordResetView.as_view(), name='account_password_reset'),
    url(
        r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        account_views.PasswordResetTokenView.as_view(),
        name='account_password_reset_token'
    ),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^ckeditor/upload/', ckperms(ckeditor_views.upload), name='ckeditor_upload'),
    url(r'^ckeditor/browse/', ckperms(ckeditor_views.browse), name='ckeditor_browse'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^', include('tn2app.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', django.views.static.serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
