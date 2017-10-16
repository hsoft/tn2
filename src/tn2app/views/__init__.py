import io

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.syndication.views import Feed
from django.core.exceptions import PermissionDenied
from django.db.models import Max, Count, Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic import ListView, TemplateView, DetailView, FormView, View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.static import serve

from PIL import Image
from post_office import mail
import account.views
import account.forms

from ..models import (
    User, UserProfile, Article, ArticleCategory, DiscussionGroup, Discussion, Project, ProjectVote,
    ArticleComment, DiscussionComment, ProjectComment, Notification, Pattern, Sponsorship
)
from ..forms import (
    UserProfileForm, NewDiscussionForm, EditDiscussionForm, CommentForm, SignupForm, ContactForm,
    UserSendMessageForm
)
from .common import ViewWithCommentsMixin, UserViewMixin, BelongsToUserMixin

class SignupView(account.views.SignupView):
    form_class = SignupForm

    @staticmethod
    def breadcrumb():
        return [(None, "Inscription")]


class LoginView(account.views.LoginView):
    form_class = account.forms.LoginEmailForm

    @staticmethod
    def breadcrumb():
        return [(None, "Connexion")]


class ChangePasswordView(account.views.ChangePasswordView):
    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['shown_user'] = self.get_user()
        return result

    @staticmethod
    def breadcrumb():
        return [(None, "Modifier mon mot de passe")]


class Homepage(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        # Affichage des trois articles de la page d'accueil:
        # En règle générale, on veut les derniers articles en ordre de parution.
        # ... sauf pour le 2e spot, qui est réservé aux trouvailles.
        # Le 3e spot, il est pour le dernier article "featured", mais ça se peut que
        # cet article n'existe pas.
        articles = Article.published\
            .exclude(categories__slug='les-trouvailles')\
            .order_by('-publish_time')
        trouvailles = Article.published\
            .filter(categories__slug='les-trouvailles')\
            .order_by('-publish_time').first()
        # Les trouvailles ont toujours le même titre sur la page d'accueil
        trouvailles.title = "Les trouvailles de la semaine"
        featured_articles = Article.published.filter(featured=True)
        if featured_articles.exists():
            featured_article = featured_articles.order_by('-publish_time').first()
            articles = [articles[0], trouvailles, featured_article]
        else:
            articles = [articles[0], trouvailles, articles[1]]
        featured_projects = Project.objects\
            .filter(featured_time__isnull=False)\
            .order_by('-featured_time')

        latest_projects = Project.objects
        recent_discussions = Discussion.objects\
            .filter(group__private=False)\
            .order_by('-last_activity')[:4]
        result.update({
            'articles': articles,
            'featured_projects': featured_projects,
            'popular_projects': Project.objects.popular_this_week(),
            'latest_projects': latest_projects,
            'recent_discussions': recent_discussions,
        })
        return result

    def get_sponsor(self):
        return Sponsorship.objects.get_random_main_page_element()


class DiscussionGroupListView(ListView):
    model = DiscussionGroup
    template_name = 'discussion_groups.html'
    paginate_by = 8

    featured_groups = DiscussionGroup.objects.filter(group_type=DiscussionGroup.TYPE_FEATURED).order_by('display_order')
    geo_groups = DiscussionGroup.objects.filter(group_type=DiscussionGroup.TYPE_GEOGRAPHICAL).order_by('display_order')
    recent_discussions = Discussion.objects.filter(group__private=False).order_by('-last_activity')

    @staticmethod
    def breadcrumb():
        return [(reverse('discussion_groups'), "Groupes")]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(group_type=DiscussionGroup.TYPE_NORMAL)
        if not self.request.user.has_perm('tn2app.access_private_groups'):
            queryset = queryset.filter(private=False)
        else:
            queryset = queryset.filter(
                Q(private=False) | Q(restrict_access_to__in=self.request.user.groups.all())
            )
        queryset = queryset.annotate(latest_activity=Max('discussions__last_activity'))\
            .order_by('-latest_activity')
        return queryset


# ref https://docs.djangoproject.com/en/1.10/topics/class-based-views/mixins/#using-singleobjectmixin-with-listview
class DiscussionGroupDetailView(SingleObjectMixin, ListView):
    slug_url_kwarg = 'group_slug'
    paginate_by = 20
    template_name = 'discussion_group.html'

    def breadcrumb(self):
        result = DiscussionGroupListView.breadcrumb()
        return result + [(None, self.object.title_display)]

    def user_can_admin(self):
        return self.request.user.has_perm('tn2app.change_discussiongroup')

    def get(self, request, *args, **kwargs):
        group = self.get_object(queryset=DiscussionGroup.objects.all())
        if not group.can_be_seen_by_user(request.user):
            raise PermissionDenied()
        self.object = group
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.object
        return context

    def get_queryset(self):
        # comment anootate() is the biggest speedup here. author__profile is a minor speedup, but
        # still...
        return self.object.discussions\
            .annotate(comment_count=Count('comments'))\
            .select_related('author__profile')\
            .order_by('-last_activity')


class DiscussionDetailView(SingleObjectMixin, ViewWithCommentsMixin, ListView):
    slug_url_kwarg = 'discussion_slug'
    paginate_by = settings.DISCUSSION_PAGINATE_BY
    template_name = 'discussion.html'

    def breadcrumb(self):
        result = DiscussionGroupListView.breadcrumb()
        discussion = self.object
        group = discussion.group
        return result + [
            (reverse('discussion_group', args=(group.slug, )), group.title_display()),
            (None, discussion.title),
        ]

    def user_can_admin(self):
        return self.request.user.has_perm('tn2app.change_discussion')

    def get(self, request, *args, **kwargs):
        discussion = self.get_object(queryset=Discussion.objects.filter(group__slug=kwargs['group_slug']))
        if discussion.group.private and not request.user.has_perm('tn2app.access_private_groups'):
            raise PermissionDenied()
        self.object = discussion

        # special case: if we have a "c" query arg, it's because we've just commented and we want
        # to see the last page... but *only* if we don't already have a 'page' arg!
        if 'page' not in request.GET and 'c' in request.GET:
            self.kwargs['page'] = 'last'
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['discussion'] = self.object
        context['group'] = self.object.group
        return context

    def get_queryset(self):
        return self.object.comments.order_by('submit_date')


class DiscussionAdd(LoginRequiredMixin, CreateView):
    template_name = 'discussion_add.html'
    form_class = NewDiscussionForm

    def breadcrumb(self):
        result = DiscussionGroupListView.breadcrumb()
        group = self.get_context_data()['group']
        return result + [
            (group.get_absolute_url(), group.title_display),
            (None, "Nouvelle discussion"),
        ]

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result['group'] = result['form'].group
        return result

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        group_slug = self.kwargs['group_slug']
        group = DiscussionGroup.objects.get(slug=group_slug)
        result['group'] = group
        result['author'] = self.request.user
        return result


class DiscussionEdit(LoginRequiredMixin, UpdateView):
    template_name = 'discussion_edit.html'
    model = Discussion
    form_class = EditDiscussionForm
    context_object_name = 'discussion'
    slug_url_kwarg = 'discussion_slug'

    def breadcrumb(self):
        result = DiscussionGroupListView.breadcrumb()
        group = self.object.group
        return result + [
            (group.get_absolute_url(), group.title_display),
            (None, "Modifier une discussion"),
        ]

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        queryset = queryset.filter(group__slug=self.kwargs['group_slug'])
        result = super().get_object(queryset=queryset)
        if result.author != self.request.user and not self.request.user.has_perm('tn2app.change_discussion'):
            raise PermissionDenied()
        return result

    def post(self, request, *args, **kwargs):
        if 'delete' in request.POST:
            discussion = self.get_object()
            group = discussion.group
            discussion.delete()
            return HttpResponseRedirect(group.get_absolute_url())
        else:
            return super().post(request, *args, **kwargs)


class ArticleMixin:
    featured_categories = ArticleCategory.objects.filter(featured=True).order_by('title')

    def active_category(self):
        return None

    def breadcrumb(self):
        return [(reverse('article_list'), "Blog")]


class ArticleDetailView(ArticleMixin, ViewWithCommentsMixin, DetailView):
    model = Article
    template_name = 'article.html'

    def breadcrumb(self):
        return super().breadcrumb() + [(None, self.get_object().title)]

    def user_can_admin(self):
        return self.request.user.has_perm('tn2app.change_article')

    def get_sponsor(self):
        return Sponsorship.objects.get_random_blog_element()


class ArticleList(ArticleMixin, ListView):
    template_name = 'article_list.html'
    model = Article
    queryset = Article.published
    ordering = '-publish_time'
    paginate_by = 5

    def get_sponsor(self):
        return Sponsorship.objects.get_random_blog_element()


class ArticlesByCategoryList(ArticleList):
    def active_category(self):
        return ArticleCategory.objects.get(slug=self.kwargs['slug'])

    def breadcrumb(self):
        result = super().breadcrumb()
        cat = self.active_category()
        return result + [(reverse('category', args=(cat.slug, )), cat.title)]

    def get_queryset(self):
        try:
            cat = self.active_category()
        except ArticleCategory.DoesNotExist:
            raise Http404()
        queryset = super().get_queryset()
        return queryset.filter(categories=cat)


class ArticlesByAuthorList(ArticleList):
    def active_author(self):
        return User.objects.get(username=self.kwargs['slug'])

    def breadcrumb(self):
        result = super().breadcrumb()
        author = self.active_author()
        return result + [(reverse('blog_by_author', args=(author.username, )), author.profile.display_name)]

    def get_queryset(self):
        try:
            author = self.active_author()
        except User.DoesNotExist:
            raise Http404()
        queryset = super().get_queryset()
        return queryset.filter(author=author)


class ArticleFeed(Feed):
    title = "Thread and needles"
    link = "/feed/"
    description = "Culture Couture"

    def items(self):
        return Article.published.all().order_by('-publish_time')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.get_excerpt()


class UserProfileView(UserViewMixin, ListView):
    template_name = 'user_profile.html'
    model = Project
    ordering = '-creation_time'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self._get_shown_user())

    def user_can_admin(self):
        return self.request.user.has_perm('tn2app.change_userprofile')


class UserFavoritesView(UserViewMixin, ListView):
    template_name = 'user_favorites.html'
    model = ProjectVote
    ordering = '-date_liked'
    paginate_by = 9

    def breadcrumb(self):
        return super().breadcrumb() + [(None, "Favoris")]

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['project_list'] = [vote.project for vote in result['projectvote_list']]
        return result

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self._get_shown_user(), favorite=True)


class UserProfileEdit(UserViewMixin, BelongsToUserMixin, UpdateView):
    USER_ATTR = 'user'
    SUPERUSER_PERM = 'tn2app.change_userprofile'

    template_name = 'user_profile_edit.html'
    model = UserProfile
    form_class = UserProfileForm
    context_object_name = 'profile'

    def breadcrumb(self):
        return super().breadcrumb() + [(None, "Modifier")]

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return self._get_shown_user().profile


class UserSendMessageView(UserViewMixin, LoginRequiredMixin, FormView):
    form_class = UserSendMessageForm
    template_name = 'user_sendmessage.html'

    def breadcrumb(self):
        return super().breadcrumb() + [(None, "Contacter")]

    def form_valid(self, form):
        to = self._get_shown_user()
        from_ = self.request.user
        mail.send(
            to.email,
            settings.DEFAULT_FROM_EMAIL,
            headers={'Reply-to': from_.email},
            template='user_sendmessage_form',
            context={
                'from': from_,
                'to': to,
                'message': form.cleaned_data['message'],
            },
        )
        return self.render_to_response(self.get_context_data(message_sent=True))


class UserNotificationsView(UserViewMixin, LoginRequiredMixin, ListView):
    template_name = 'user_notifications.html'
    model = Notification

    def _get_shown_user(self):
        return self.request.user

    def breadcrumb(self):
        return super().breadcrumb() + [(None, "Notifications")]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.profile.has_notifications:
            user.profile.has_notifications = False
            user.profile.save()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self._get_shown_user().notifications.all()


class PageView(TemplateView):
    pagename = None

    def get_template_names(self):
        return ["pages/{}.html".format(self.pagename)]


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'pages/contact.html'

    def form_valid(self, form):
        mail.send(
            settings.DEFAULT_FROM_EMAIL,
            form.cleaned_data['email'],
            template='contact_form',
            context=form.cleaned_data,
        )
        return self.render_to_response(self.get_context_data(message_sent=True))


class CommentViewMixin:
    def get_model(self):
        modelname = self.kwargs['model']
        return {
            'article': ArticleComment,
            'discussion': DiscussionComment,
            'project': ProjectComment,
        }[modelname]

    def get_object(self):
        model = self.get_model()
        return model.objects.get(id=self.kwargs['comment_pk'])


class CommentAdd(LoginRequiredMixin, CommentViewMixin, View):
    TARGET_MODEL_VIEW = None
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        model = self.get_model().target.field.rel.to
        target = model.objects.get(id=self.kwargs['model_pk'])
        form = CommentForm(request.POST)
        if form.is_valid():
            # Don't allow duplicate comments
            duplicate = False
            from_same_user = target.comments.filter(user=request.user)
            if from_same_user.exists():
                if from_same_user.last().comment == form.cleaned_data['comment']:
                    duplicate = True
            if not duplicate:
                new_comment = target.comments.create(
                    user=request.user,
                    comment=form.cleaned_data['comment'],
                )
                if hasattr(target, 'update_last_activity'):
                    target.update_last_activity()
                return HttpResponseRedirect(new_comment.get_absolute_url())
        return HttpResponseRedirect(target.get_absolute_url())


class CommentEdit(BelongsToUserMixin, CommentViewMixin, FormView):
    USER_ATTR = 'user'
    SUPERUSER_PERM = 'tn2app.change_articlecomment'

    template_name = 'comment_edit.html'
    form_class = CommentForm

    def get_initial(self):
        return {'comment': self.get_object().comment}

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = self.get_object()
            comment.comment = form.cleaned_data['comment']
            comment.save()
        return HttpResponseRedirect(comment.get_absolute_url())


class CommentDelete(BelongsToUserMixin, CommentViewMixin, View):
    USER_ATTR = 'user'
    SUPERUSER_PERM = 'tn2app.change_articlecomment'

    def get(self, request, *args, **kwargs):
        comment = self.get_object()
        parent_obj = comment.target
        following_comment = comment.get_next()
        if not following_comment:
            following_comment = comment.get_prev()
        if following_comment:
            success_url = following_comment.get_absolute_url()
        else:
            success_url = parent_obj.get_absolute_url()
        comment.delete()
        if hasattr(parent_obj, 'update_last_activity'):
            parent_obj.update_last_activity()
        return HttpResponseRedirect(success_url)


# Full-Text search is a bit intensive, resource-wise. To minimize the risk of the server being
# brought down to its knees simply because a bot decides that it searches a couple of things,
# we're making the search available to logged users only. Later, we can work on making it more
# efficient and remove that limitation.

class BaseSearchView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        q = self.request.GET.get('q')
        if not q:
            return self.model.objects.none()
        return self.model.objects.full_text_search(q)


class ArticleSearchView(BaseSearchView):
    model = Article
    template_name = 'search_article.html'
    paginate_by = 10

    def breadcrumb(self):
        return [(None, "Recherche d'articles")]


class ProjectSearchView(BaseSearchView):
    model = Project
    template_name = 'search_project.html'
    paginate_by = 15

    def breadcrumb(self):
        return [(None, "Recherche projets")]


class DiscussionSearchView(BaseSearchView):
    model = Discussion
    template_name = 'search_discussion.html'
    paginate_by = 10

    def breadcrumb(self):
        return [(None, "Recherche de discussions")]


class CompoundSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'search_compound.html'

    def breadcrumb(self):
        return [(None, "Recherche de '{}'".format(self.request.GET.get('q')))]

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        q = self.request.GET.get('q')
        if q:
            article_qs = Article.objects.full_text_search(q)
            project_qs = Project.objects.full_text_search(q)
            discussion_qs = Discussion.objects.full_text_search(q)
            user_qs = UserProfile.objects.full_text_search(q)
        else:
            article_qs = Article.objects.none()
            project_qs = Project.objects.none()
            discussion_qs = Discussion.objects.none()
            user_qs = UserProfile.objects.none()
        result['search_query'] = q
        result['article_qs'] = article_qs
        result['project_qs'] = project_qs
        result['discussion_qs'] = discussion_qs
        result['user_qs'] = user_qs
        return result

# AJAX

class PatternListJSON(View):
    def get(self, request, *args, **kwargs):
        qs = Pattern.objects.filter(creator_id=kwargs['creator_id'])
        return JsonResponse({
            'objects': list(qs.values_list('id', 'name', 'target', 'domain', 'category_id')),
        })

# Debug views

# This doesn't give good thumbnails at all! but we don't care. It's just for debugging. We really
# don't want to copy thumbnail+crop algo, which is more complex. nginx is the one taking care of
# doing the real thumbnailing. All we care here is gettingimages of the right size to use as
# placeholders.
def serve_thumbnail(request, width, height, path):
    if not settings.DEBUG:
        raise PermissionDenied()
    try:
        response = serve(request, path, document_root=settings.MEDIA_ROOT)
    except Exception:
        return HttpResponseRedirect(settings.MEDIA_DEBUG_REDIRECT_TO + request.get_full_path())
    if hasattr(response, 'file_to_stream'):
        img = Image.open(response.file_to_stream)
        img.thumbnail((int(width), int(height)))
        fp = io.BytesIO()
        img.save(fp, format=img.format)
        fp.seek(0)
        response.streaming_content = fp
    return response

def serve_media(request, path):
    if not settings.DEBUG:
        raise PermissionDenied()
    try:
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    except Exception:
        return HttpResponseRedirect(settings.MEDIA_DEBUG_REDIRECT_TO + request.get_full_path())

