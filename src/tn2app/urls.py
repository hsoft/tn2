from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^blog/$', views.ArticleList.as_view(), name='article_list'),
    url(r'^blog/(?P<slug>[-%’\w]+)/$', views.article, name='article'),
    url(
        r'^blog/categorie/(?P<slug>[-\w]+)/$',
        views.ArticlesByCategoryList.as_view(),
        name='category'
    ),
    url(r'^projets-couture/$', views.ProjectList.as_view(), name='project_list'),
    url(
        r'^projets-couture/(?P<pk>\d+)-(?P<slug>[-\w]+)$',
        views.ProjectDetails.as_view(),
        name='project_details'
    ),
    url(r'^groupes/$', views.discussion_groups, name='discussion_groups'),
    # the "%" and "’" characters aren't part of django's slug, but it's part of our "legacy" slugs.
    url(r'^groupes/(?P<group_slug>[-%’\w]+)/home/$', views.discussion_group, name='discussion_group'),
    url(r'^groupes/(?P<group_slug>[-%’\w]+)/forum/topic/add/$', views.DiscussionAdd.as_view(), name='discussion_add'),
    url(
        r'^groupes/(?P<group_slug>[-%’\w]+)/forum/topic/(?P<discussion_slug>[-%’\w]+)/$',
        views.discussion,
        name='discussion'
    ),
    url(
        r'^groupes/(?P<group_slug>[-%’\w]+)/forum/topic/(?P<discussion_slug>[-%’\w]+)/edit/$',
        views.DiscussionEdit.as_view(),
        name='discussion_edit'
    ),
    url(r'^comments/(?P<pk>\d+)/edit/$', views.CommentEdit.as_view(), name='comment_edit'),
    url(r'^members/(?P<username>[-\w]+)/profil/$', views.UserProfile.as_view(), name='user_profile'),
]

