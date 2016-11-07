from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^blog/(?P<slug>[-\w]+)/$', views.article, name='article'),
    url(r'^groupes/$', views.discussion_groups, name='discussion_groups'),
    url(r'^groupes/(?P<group_slug>[-\w]+)/home/$', views.discussion_group, name='discussion_group'),
    url(r'^groupes/(?P<group_slug>[-\w]+)/forum/topic/add/$', views.DiscussionAdd.as_view(), name='discussion_add'),
    url(r'^groupes/(?P<group_slug>[-\w]+)/forum/topic/(?P<discussion_slug>[-\w]+)$', views.discussion, name='discussion'),
]

