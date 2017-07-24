from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    url(r'^$', views.Homepage.as_view(), name='homepage'),
    url(r'^blog/$', views.ArticleList.as_view(), name='article_list'),
    url(r'^blog/(?P<slug>[-%’\w]+)/$', views.ArticleDetailView.as_view(), name='article'),
    url(
        r'^blog/categorie/(?P<slug>[-\w]+)/$',
        views.ArticlesByCategoryList.as_view(),
        name='category'
    ),
    url(
        r'^blog/author/(?P<slug>[-\w]+)/$',
        views.ArticlesByAuthorList.as_view(),
        name='blog_by_author'
    ),
    url(r'^feed/', views.ArticleFeed(), name='blog_feed'),
    url(r'^projets-couture/$', views.ProjectList.as_view(), name='project_list'),
    url(
        r'^projets-couture/(?P<pk>\d+)-(?P<slug>[-\w]*)/$',
        views.ProjectDetails.as_view(),
        name='project_details'
    ),
    url(
        r'^projets-couture/(?P<pk>\d+)-(?P<slug>[-\w]*)/edit/$',
        views.ProjectEdit.as_view(),
        name='project_edit'
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
    url(r'^comments/(?P<model>\w+)/(?P<model_pk>\d+)/add/$', views.CommentAdd.as_view(), name='comment_add'),
    url(r'^comments/(?P<model>\w+)/(?P<comment_pk>\d+)/edit/$', views.CommentEdit.as_view(), name='comment_edit'),
    url(
        r'^membres/(?P<username>[-\w]+)/profil/$',
        views.UserProfileView.as_view(),
        name='user_profile'
    ),
    url(
        r'^membres/(?P<username>[-\w]+)/$',
        RedirectView.as_view(pattern_name='user_profile'),
        name='user_profile_redirect'
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
        r'^notifications/$',
        views.UserNotificationsView.as_view(),
        name='user_notifications',
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

    url(r'^ajax/patterns/(?P<creator_id>\d+)/$', views.PatternListJSON.as_view(), name='ajax_patterns'),

    url(r'^thumb/(?P<width>\d+)/(?P<height>\d+)/(?P<path>.*)$', views.serve_thumbnail, name='thumbnail'),
]

PAGES = [
    'a-propos', 'cgu', 'foire-aux-questions', 'presse', 'sponsors',
    'envoyez-nous-vos-articles', 'soutenir',
]

urlpatterns += [
    url(r'^{}/$'.format(p), views.PageView.as_view(pagename=p), name='page_{}'.format(p))
    for p in PAGES
]

