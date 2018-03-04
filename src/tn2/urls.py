from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy

from ckeditor_uploader import views as ckeditor_views
from tn2app import views as tn2_views
from tn2app.views import user as tn2_user_views

ckperms = user_passes_test(lambda user: user.has_perm('tn2app.add_article'))

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # accounts overrides
    # These URLs are already in accounts include below but we want to change
    # the linked views of some of them without having to redefine the whole
    # thing. We intentionally don't name these URLs to avoid name clashes.
    url(r'^accounts/login/$',
        tn2_user_views.LoginView.as_view(
        template_name='registration/login.html'),
    ),
    url(r'^accounts/password/change/$',
        tn2_user_views.ChangePasswordView.as_view(
        success_url=reverse_lazy('auth_password_change_done'))
    ),
    url(r'^accounts/password/change/done/$',
        tn2_user_views.ChangePasswordView.as_view(done=True)
    ),
    # accounts include
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^ckeditor/upload/', ckperms(ckeditor_views.upload), name='ckeditor_upload'),
    url(r'^ckeditor/browse/', ckperms(ckeditor_views.browse), name='ckeditor_browse'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^', include('tn2app.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', tn2_views.serve_media),
    ]
