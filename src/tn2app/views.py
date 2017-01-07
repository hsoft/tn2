import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Max, Count
from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView, RedirectView, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from django_comments.models import Comment
from post_office import mail
import account.views

from .models import (
    UserProfile, Article, ArticleCategory, DiscussionGroup, Discussion, Project, ProjectVote,
    ProjectCategory
)
from .forms import (
    UserProfileForm, NewDiscussionForm, EditDiscussionForm, EditCommentForm, NewProjectForm,
    SignupForm, ContactForm, UserSendMessageForm
)

class SignupView(account.views.SignupView):
    form_class = SignupForm


def homepage(request):
    articles = Article.published.order_by('-creation_time')[:3]
    featured_projects = Project.objects.filter(featured_time__isnull=False).order_by('-featured_time')
    popular_projects = Project.objects.annotate(num_likes=Count('likes')).order_by('-num_likes')
    latest_projects = Project.objects
    recent_discussions = Discussion.objects.filter(group__private=False)\
        .order_by('-last_activity')[:4]
    context = {
        'articles': articles,
        'featured_projects': featured_projects,
        'popular_projects': popular_projects,
        'latest_projects': latest_projects,
        'recent_discussions': recent_discussions,
    }
    return render(request, 'homepage.html', context)

class DiscussionGroupListView(ListView):
    model = DiscussionGroup
    template_name = 'discussion_groups.html'
    paginate_by = 8

    featured_groups = DiscussionGroup.objects.filter(group_type=DiscussionGroup.TYPE_FEATURED)
    geo_groups = DiscussionGroup.objects.filter(group_type=DiscussionGroup.TYPE_GEOGRAPHICAL)
    recent_discussions = Discussion.objects.filter(group__private=False).order_by('-last_activity')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(group_type=DiscussionGroup.TYPE_NORMAL)
        if not self.request.user.has_perm('tn2app.access_private_groups'):
            queryset = queryset.filter(private=False)
        queryset = queryset.annotate(latest_activity=Max('discussions__last_activity'))\
            .order_by('-latest_activity')
        return queryset


# ref https://docs.djangoproject.com/en/1.10/topics/class-based-views/mixins/#using-singleobjectmixin-with-listview
class DiscussionGroupDetailView(SingleObjectMixin, ListView):
    slug_url_kwarg = 'group_slug'
    paginate_by = 20
    template_name = 'discussion_group.html'

    def get(self, request, *args, **kwargs):
        group = self.get_object(queryset=DiscussionGroup.objects.all())
        if group.private and not request.user.has_perm('tn2app.access_private_groups'):
            raise PermissionDenied()
        self.object = group
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.object
        return context

    def get_queryset(self):
        return self.object.discussions.order_by('-last_activity')


class DiscussionDetailView(SingleObjectMixin, ListView):
    slug_url_kwarg = 'discussion_slug'
    paginate_by = 15
    template_name = 'discussion.html'

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
        return context

    def get_queryset(self):
        return self.object.comments.order_by('submit_date')


class DiscussionAdd(LoginRequiredMixin, CreateView):
    template_name = 'discussion_add.html'
    form_class = NewDiscussionForm

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

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        queryset = queryset.filter(group__slug=self.kwargs['group_slug'])
        result = super().get_object(queryset=queryset)
        if result.author != self.request.user:
            raise PermissionDenied()
        return result


class ArticleMixin:
    featured_categories = ArticleCategory.objects.filter(featured=True).order_by('title')


class ArticleDetailView(ArticleMixin, DetailView):
    model = Article
    template_name = 'article.html'


class ArticleList(ArticleMixin, ListView):
    template_name = 'article_list.html'
    model = Article
    queryset = Article.published
    ordering = '-creation_time'
    paginate_by = 5



class ArticlesByCategoryList(ArticleList):
    def get_queryset(self):
        try:
            cat = ArticleCategory.objects.get(slug=self.kwargs['slug'])
        except ArticleCategory.DoesNotExist:
            raise Http404()
        queryset = super().get_queryset()
        return queryset.filter(categories=cat)


class CommentEdit(UserPassesTestMixin, UpdateView):
    template_name = 'comment_edit.html'
    model = Comment
    form_class = EditCommentForm
    context_object_name = 'comment'

    # for UserPassesTestMixin
    raise_exception = True

    def test_func(self):
        return self.request.user == self.get_object().user


class UserViewMixin:
    def _get_shown_user(self):
        User = get_user_model()
        try:
            return User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            raise Http404()


class UserProfileView(UserViewMixin, ListView):
    template_name = 'user_profile.html'
    model = Project
    ordering = '-creation_time'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['shown_user'] = self._get_shown_user()
        return result

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self._get_shown_user())


class UserProfileEdit(UserViewMixin, UserPassesTestMixin, UpdateView):
    template_name = 'user_profile_edit.html'
    model = UserProfile
    form_class = UserProfileForm
    context_object_name = 'profile'

    # for UserPassesTestMixin
    raise_exception = True

    def test_func(self):
        u = self.request.user
        return u == self.get_object().user or u.has_perm('tn2app.change_userprofile')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return self._get_shown_user().profile


class UserSendMessageView(UserViewMixin, LoginRequiredMixin, FormView):
    form_class = UserSendMessageForm
    template_name = 'user_sendmessage.html'

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['shown_user'] = self._get_shown_user()
        return result

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


class ProjectList(ListView):
    template_name = 'project_list.html'
    model = Project
    paginate_by = 15

    categories = ProjectCategory.objects

    def active_order(self):
        result = self.request.GET.get('order')
        if result not in {'latest', 'popular', 'random'}:
            result = 'latest'
        return result

    def active_category(self):
        catid = self.request.GET.get('category')
        if not catid:
            return None
        try:
            return ProjectCategory.objects.get(id=catid)
        except ProjectCategory.DoesNotExist:
            return None

    def get_ordering(self):
        order = self.active_order()
        if order == 'popular':
            return '-num_likes'
        elif order == 'random':
            return '?'
        else:
            return '-creation_time'

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.active_category()
        if category:
            queryset = queryset.filter(category=category)
        order = self.active_order()
        if order == 'popular':
            queryset = queryset.annotate(num_likes=Count('likes'))
        elif order == 'random':
            # We only want one page of this, paginating is irrelevant here.
            queryset = queryset[:self.paginate_by]
        return queryset


class ProjectDetails(DetailView):
    template_name = 'project_details.html'
    model = Project

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['is_liked'] = result['project'].likes.filter(pk=self.request.user.id).exists()
        return result


class ProjectCreate(LoginRequiredMixin, CreateView):
    template_name = 'project_create.html'
    form_class = NewProjectForm

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
            ProjectVote.objects.create(user=self.request.user, project=project)
        except IntegrityError:
            # double like, ignore
            pass


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


class ProjectSearchView(BaseSearchView):
    model = Project
    template_name = 'search_project.html'
    paginate_by = 15


class DiscussionSearchView(BaseSearchView):
    model = Discussion
    template_name = 'search_discussion.html'
    paginate_by = 10


class CompoundSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'search_compound.html'

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        q = self.request.GET.get('q')
        if q:
            article_qs = Article.objects.full_text_search(q)
            project_qs = Project.objects.full_text_search(q)
            discussion_qs = Discussion.objects.full_text_search(q)
        else:
            article_qs = Article.objects.none()
            project_qs = Project.objects.none()
            discussion_qs = Discussion.objects.none()
        result['search_query'] = q
        result['article_qs'] = article_qs
        result['project_qs'] = project_qs
        result['discussion_qs'] = discussion_qs
        return result

