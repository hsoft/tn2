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
        r'^projets-couture/(?P<pk>\d+)-(?P<slug>[-\w]*)$',
        views.ProjectDetails.as_view(),
        name='project_details'
    ),
    url(
        r'^projets-couture/(?P<pk>\d+)-(?P<slug>[-\w]*)/like/$',
        views.ProjectLike.as_view(),
        name='project_like'
    ),
    url(
        r'^projets-couture/(?P<pk>\d+)-(?P<slug>[-\w]*)/feature/$',
        views.ProjectFeature.as_view(),
        name='project_feature'
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
    url(
        r'^membres/(?P<username>[-\w]+)/profil/$',
        views.UserProfileView.as_view(),
        name='user_profile'
    ),
    url(
        r'^membres/(?P<username>[-\w]+)/profil/edit/$',
        views.UserProfileEdit.as_view(),
        name='user_profile_edit'
    ),
    url(
        r'^membres/(?P<username>[-\w]+)/projets-couture/nouveau-projet/$',
        views.ProjectCreate.as_view(),
        name='project_create'
    ),
    url(
        r'^search/$',
        views.CompoundSearchView.as_view(),
        name='search',
    ),
    url(
        r'^search/articles/$',
        views.ArticleSearchView.as_view(),
        name='search_article',
    ),
    url(
        r'^search/projets/$',
        views.ProjectSearchView.as_view(),
        name='search_project',
    ),
    url(
        r'^search/discussions/$',
        views.DiscussionSearchView.as_view(),
        name='search_discussion',
    ),

    # pages
    url(r'^contact/$', views.PageView.as_view(pagename='contact'), name='contact'),
]

PAGES = ['a-propos', 'cgu', 'foire-aux-questions', 'contact', 'presse', 'sponsors', 'mentions-legales']

urlpatterns += [
    url(r'^{}/$'.format(p), views.PageView.as_view(pagename=p), name='page_{}'.format(p))
    for p in PAGES
]

