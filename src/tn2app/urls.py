from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^blog/$', views.ArticleList.as_view(), name='article_list'),
    url(r'^blog/(?P<slug>[-%’\w]+)/$', views.ArticleDetailView.as_view(), name='article'),
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
        r'^projets-couture/(?P<pk>\d+)-(?P<slug>[-\w]*)/jaime/$',
        views.ProjectLike.as_view(),
        name='project_like'
    ),
    url(
        r'^projets-couture/(?P<pk>\d+)-(?P<slug>[-\w]*)/favoris/$',
        views.ProjectFavorite.as_view(),
        name='project_favorite'
    ),
    url(
        r'^projets-couture/(?P<pk>\d+)-(?P<slug>[-\w]*)/a-la-une/$',
        views.ProjectFeature.as_view(),
        name='project_feature'
    ),
    url(r'^groupes/$', views.DiscussionGroupListView.as_view(), name='discussion_groups'),
    # the "%" and "’" characters aren't part of django's slug, but it's part of our "legacy" slugs.
    url(
        r'^groupes/(?P<group_slug>[-%’\w]+)/home/$',
        views.DiscussionGroupDetailView.as_view(),
        name='discussion_group'
    ),
    url(r'^groupes/(?P<group_slug>[-%’\w]+)/forum/topic/add/$', views.DiscussionAdd.as_view(), name='discussion_add'),
    url(
        r'^groupes/(?P<group_slug>[-%’\w]+)/forum/topic/(?P<discussion_slug>[-%’\w]+)/$',
        views.DiscussionDetailView.as_view(),
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
        r'^membres/(?P<username>[-\w]+)/favoris/$',
        views.UserFavoritesView.as_view(),
        name='user_favorites'
    ),
    url(
        r'^membres/(?P<username>[-\w]+)/contacter/$',
        views.UserSendMessageView.as_view(),
        name='user_sendmessage'
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

    url(r'^contact/$', views.ContactView.as_view(), name='page_contact'),
]

PAGES = [
    'a-propos', 'cgu', 'foire-aux-questions', 'presse', 'sponsors', 'mentions-legales',
    'envoyez-nous-vos-articles',
]

urlpatterns += [
    url(r'^{}/$'.format(p), views.PageView.as_view(pagename=p), name='page_{}'.format(p))
    for p in PAGES
]

