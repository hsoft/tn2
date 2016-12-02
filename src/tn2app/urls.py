from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^blog/$', views.ArticleList.as_view(), name='article_list'),
    url(r'^blog/(?P<slug>[-\w]+)/$', views.article, name='article'),
    url(r'^groupes/$', views.discussion_groups, name='discussion_groups'),
    url(r'^groupes/(?P<group_slug>[-\w]+)/home/$', views.discussion_group, name='discussion_group'),
    url(r'^groupes/(?P<group_slug>[-\w]+)/forum/topic/add/$', views.DiscussionAdd.as_view(), name='discussion_add'),
    url(
        r'^groupes/(?P<group_slug>[-\w]+)/forum/topic/(?P<discussion_slug>[-\w]+)/$',
        views.discussion,
        name='discussion'
    ),
    url(
        r'^groupes/(?P<group_slug>[-\w]+)/forum/topic/(?P<discussion_slug>[-\w]+)/edit/$',
        views.DiscussionEdit.as_view(),
        name='discussion_edit'
    ),
    url(r'^redaction/new-article/$', views.ArticleAdd.as_view(), name='article_add'),
    url(r'^redaction/edit-article/(?P<slug>[-\w]+)/$', views.ArticleEdit.as_view(), name='article_edit'),
    url(r'^comments/(?P<pk>\d+)/edit/$', views.CommentEdit.as_view(), name='comment_edit'),
]

