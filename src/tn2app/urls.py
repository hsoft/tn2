from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^blog/(?P<slug>[-\w]+)/$', views.article, name='article'),
]

