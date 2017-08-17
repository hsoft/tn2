import datetime
import io

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.syndication.views import Feed
from django.core.exceptions import PermissionDenied
from django.db.models import Max, Count, Q
from django.forms.widgets import Select
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import ListView, TemplateView, DetailView, RedirectView, FormView, View
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.static import serve

from PIL import Image
from post_office import mail
import account.views
import account.forms

from .models import (
    User, UserProfile, Article, ArticleCategory, DiscussionGroup, Discussion, Project, ProjectVote,
    ArticleComment, DiscussionComment, ProjectComment, Notification, Pattern, PatternCategory,
    PatternCreator,
)
from .forms import (
    UserProfileForm, NewDiscussionForm, EditDiscussionForm, CommentForm, ProjectForm,
    SignupForm, ContactForm, UserSendMessageForm
)
from .util import href
from .widgets import UnrolledTwoColsSelect

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


class ViewWithCommentsMixin:
    def get_comment_form(self):
        return CommentForm()


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


class ArticleList(ArticleMixin, ListView):
    template_name = 'article_list.html'
    model = Article
    queryset = Article.published
    ordering = '-publish_time'
    paginate_by = 5


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


class UserViewMixin(ContextMixin):
    def _get_shown_user(self):
        try:
            return User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            raise Http404()

    def breadcrumb(self):
        u = self._get_shown_user()
        return [(reverse('user_profile', args=(u.username, )), u.profile.display_name)]

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['shown_user'] = self._get_shown_user()
        return result


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


class BelongsToUserMixin(UserPassesTestMixin):
    USER_ATTR = None
    SUPERUSER_PERM = None
    raise_exception = True

    def test_func(self):
        u = self.request.user
        return u == getattr(self.get_object(), self.USER_ATTR) or u.has_perm(self.SUPERUSER_PERM)


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


class ProjectList(ListView):
    template_name = 'project_list.html'
    model = Project
    paginate_by = 15

    def active_order(self):
        result = self.request.GET.get('order')
        if result not in {'latest', 'popular', 'random'}:
            result = 'latest'
        return result

    def target_selector(self):
        return UnrolledTwoColsSelect(
            self.request,
            Pattern.TARGET_CHOICES,
            'target',
        ).render()

    def domain_selector(self):
        return UnrolledTwoColsSelect(
            self.request,
            Pattern.DOMAIN_CHOICES,
            'domain',
        ).render()

    def category_selector(self):
        return UnrolledTwoColsSelect(
            self.request,
            PatternCategory.objects.values_list('id', 'name'),
            'category',
        ).render()

    def pattern_selectors(self):
        item_all = [(0, "Tous")]
        creator_qs = PatternCreator.objects\
            .annotate(pattern_count=Count('patterns'))\
            .filter(pattern_count__gt=0)
        params = self.request.GET.copy()
        params['page'] = '1'

        def pop(key):
            val = params.pop(key, None)
            if isinstance(val, list):
                val = val[0] if val else None
            return val

        pattern_id = pop('pattern')
        pattern_creator_id = pop('pattern_creator')
        if pattern_id and Pattern.objects.filter(id=pattern_id).exists():
            # More reliable than the request argument.
            pattern_creator_id = Pattern.objects.get(id=pattern_id).creator.id

        get_url = '?{}&pattern_creator='.format(params.urlencode())
        widget = Select(
            attrs={'data-get-url': get_url},
            choices=item_all + list(creator_qs.values_list('id', 'name')),
        )
        result = [widget.render(
            name='pattern_creator',
            value=pattern_creator_id,
        )]
        if pattern_creator_id and PatternCreator.objects.filter(id=pattern_creator_id).exists():
            pattern_creator = PatternCreator.objects.get(id=pattern_creator_id)
            pattern_qs = pattern_creator.patterns
            params['pattern_creator'] = pattern_creator_id
            get_url = '?{}&pattern='.format(params.urlencode())
            widget = Select(
                attrs={'data-get-url': get_url},
                choices=item_all + list(pattern_qs.values_list('id', 'name')),
            )
            result.append(widget.render(
                name='pattern',
                value=pattern_id,
            ))

        return result

    def popular_this_week(self):
        return Project.objects.popular_this_week()

    @staticmethod
    def breadcrumb():
        return [(reverse('project_list'), "Projets couture")]

    def get_ordering(self):
        order = self.active_order()
        if order == 'popular':
            return '-num_likes'
        elif order == 'random':
            return '?'
        else:
            return '-creation_time'

    def get_queryset(self):

        def get(argname):
            try:
                return int(self.request.GET.get(argname))
            except (ValueError, TypeError):
                return None

        queryset = super().get_queryset()
        ARGSMAP = {
            'category': 'category_id',
            'domain': 'domain',
            'target': 'target',
            'pattern_creator': 'pattern__creator',
            'pattern': 'pattern_id',
        }
        filters = {v: get(k) for k, v in ARGSMAP.items() if get(k)}
        if filters:
            queryset = queryset.filter(**filters)
        order = self.active_order()
        if order == 'popular':
            queryset = queryset.annotate(num_likes=Count('likes'))
        elif order == 'random':
            # We only want one page of this, paginating is irrelevant here.
            queryset = queryset[:self.paginate_by]
        return queryset


class ProjectDetails(ViewWithCommentsMixin, DetailView):
    template_name = 'project_details.html'
    model = Project

    def breadcrumb(self):
        return ProjectList.breadcrumb() + [(None, self.get_object().title)]

    def user_can_admin(self):
        return self.request.user.has_perm('tn2app.change_project')

    def is_liked(self):
        return self.get_object().likes.filter(pk=self.request.user.id).exists()

    def is_favorite(self):
        try:
            return ProjectVote.objects.get(
                project=self.get_object(), user=self.request.user.id
            ).favorite
        except ProjectVote.DoesNotExist:
            return False

    def myprojects(self):
        current = self.get_object()
        return current.author.projects.exclude(id=current.id)

    def category_links(self):

        def l(argname, arg, name):
            return href(
                '{}?{}={}'.format(reverse('project_list'), argname, arg), name
            )

        project = self.get_object()
        links = []
        if project.category:
            links.append(l('category', project.category.id, project.category.name))
        links.append(l('target', project.target, project.get_target_display()))
        links.append(l('domain', project.domain, project.get_domain_display()))
        return mark_safe(', '.join(links))

    def pattern_link(self):
        project = self.get_object()
        if project.pattern:
            name = project.pattern.name
            url = project.pattern.url
        else:
            name = project.pattern_name
            url = project.pattern_url
            if url and not url.startswith('http'):
                url = 'http://{}'.format(url)
        if url:
            return href(url, name, newwindow=True)
        else:
            return name

    def creator_link(self):
        project = self.get_object()
        if project.pattern:
            creator = project.pattern.creator
            if creator:
                if creator.url:
                    return href(creator.url, creator.name, newwindow=True)
                else:
                    return creator.name

    def allprojects(self):
        # it's a really strange query that is made in the old app: it's 3 items with, in the middle,
        # the current project. Then, on the left, the project created just before it, and on the
        # right, the project created after it. Well... let's do the same thing.
        current = self.get_object()
        q1 = self.model.objects.filter(id__lt=current.id).order_by('-id')
        q2 = self.model.objects.filter(id__gt=current.id).order_by('id')
        if q1.exists() and q2.exists():
            return [q1.first(), current, q2.first()]
        elif not q1.exists():
            return [current] + list(q2.all()[:2])
        else:
            return list(q1.all()[:2]) + [current]


class ProjectEdit(BelongsToUserMixin, UpdateView):
    USER_ATTR = 'author'
    SUPERUSER_PERM = 'tn2app.change_project'

    template_name = 'project_edit.html'
    form_class = ProjectForm
    model = Project

    def breadcrumb(self):
        project = self.get_object()
        return ProjectList.breadcrumb() + [
            (project.get_absolute_url(), project.title),
            (None, "Modifier"),
        ]

    def post(self, request, *args, **kwargs):
        if 'delete' in request.POST:
            project = self.get_object()
            success_url = project.author.profile.get_absolute_url()
            project.delete()
            return HttpResponseRedirect(success_url)
        else:
            return super().post(request, *args, **kwargs)


class ProjectCreate(LoginRequiredMixin, UserViewMixin, CreateView):
    template_name = 'project_create.html'
    form_class = ProjectForm

    def breadcrumb(self):
        return super().breadcrumb() + [(None, "Publier un projet")]

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result['author'] = self.request.user
        return result


class ProjectAction(RedirectView):
    pattern_name = 'project_details'

    def _do_project_action(self, project):
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        try:
            project = Project.objects.get(pk=kwargs['pk'])
        except Project.DoesNotExist:
            raise Http404()
        self._do_project_action(project)
        return result


class ProjectLike(LoginRequiredMixin, ProjectAction):
    def _do_project_action(self, project):
        try:
            ProjectVote.objects.get(user=self.request.user, project=project).delete()
        except ProjectVote.DoesNotExist:
            vote = ProjectVote.objects.create(user=self.request.user, project=project)
            Notification.objects.notify_of_project_vote(vote)


class ProjectFavorite(LoginRequiredMixin, ProjectAction):
    def _do_project_action(self, project):
        vote, _ = ProjectVote.objects.get_or_create(user=self.request.user, project=project)
        vote.favorite = not vote.favorite
        vote.date_liked = datetime.datetime.now()
        vote.save()


class ProjectFeature(UserPassesTestMixin, ProjectAction):
    # for UserPassesTestMixin
    raise_exception = True

    def test_func(self):
        return self.request.user.has_perm('tn2app.change_project')

    def _do_project_action(self, project):
        project.featured_time = datetime.datetime.now()
        project.save()


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

    def get_object(self):
        model = self.get_model()
        return model.objects.get(id=self.kwargs['comment_pk'])

    def get_initial(self):
        return {'comment': self.get_object().comment}

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        if 'delete' in request.POST:
            parent_obj = comment.target
            success_url = parent_obj.get_absolute_url()
            comment.delete()
            if hasattr(parent_obj, 'update_last_activity'):
                parent_obj.update_last_activity()
            return HttpResponseRedirect(success_url)
        else:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = self.get_object()
                comment.comment = form.cleaned_data['comment']
                comment.save()
            return HttpResponseRedirect(comment.get_absolute_url())


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
    response = serve(request, path, document_root=settings.MEDIA_ROOT)
    if hasattr(response, 'file_to_stream'):
        img = Image.open(response.file_to_stream)
        img.thumbnail((int(width), int(height)))
        fp = io.BytesIO()
        img.save(fp, format=img.format)
        fp.seek(0)
        response.streaming_content = fp
    return response

