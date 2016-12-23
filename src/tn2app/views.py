from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Max
from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView, RedirectView
from django.views.generic.edit import CreateView, UpdateView

from django_comments.models import Comment
import account.views

from .models import (
    UserProfile, Article, ArticleCategory, DiscussionGroup, Discussion, Project, ProjectVote
)
from .forms import (
    UserProfileForm, NewDiscussionForm, EditDiscussionForm, EditCommentForm, NewProjectForm,
    SignupForm
)

class SignupView(account.views.SignupView):
    form_class = SignupForm


def homepage(request):
    articles = Article.published.order_by('-creation_time')[:3]
    featured_projects = Project.objects.all()[:5]
    context = {
        'articles': articles,
        'featured_projects': featured_projects,
    }
    return render(request, 'homepage.html', context)

def article(request, slug):
    article = Article.objects.get(slug=slug)
    context = {'article': article}
    return render(request, 'article.html', context)

def discussion_groups(request):
    groups = DiscussionGroup.objects.filter(group_type=DiscussionGroup.TYPE_NORMAL)
    if not request.user.has_perm('tn2app.access_private_groups'):
        groups = groups.filter(private=False)
    groups = groups.annotate(latest_activity=Max('discussions__last_activity')).order_by('-latest_activity')
    featured_groups = DiscussionGroup.objects.filter(group_type=DiscussionGroup.TYPE_FEATURED)
    context = {
        'groups': groups,
        'featured_groups': featured_groups.all(),
    }
    return render(request, 'discussion_groups.html', context)

def discussion_group(request, group_slug):
    group = DiscussionGroup.objects.get(slug=group_slug)
    if group.private and not request.user.has_perm('tn2app.access_private_groups'):
        raise PermissionDenied()
    discussions = group.discussions.order_by('-last_activity')
    context = {
        'group': group,
        'discussions': discussions,
    }
    return render(request, 'discussion_group.html', context)

def discussion(request, group_slug, discussion_slug):
    discussion = Discussion.objects.get(group__slug=group_slug, slug=discussion_slug)
    if discussion.group.private and not request.user.has_perm('tn2app.access_private_groups'):
        raise PermissionDenied()
    context = {
        'discussion': discussion,
        'user': request.user,
    }
    return render(request, 'discussion.html', context)

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


class ArticleList(ListView):
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


class UserProfileView(TemplateView):
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        User = get_user_model()
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            raise Http404()
        result['shown_user'] = user
        return result


class UserProfileEdit(UserPassesTestMixin, UpdateView):
    template_name = 'user_profile_edit.html'
    model = UserProfile
    form_class = UserProfileForm
    context_object_name = 'profile'

    # for UserPassesTestMixin
    raise_exception = True

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        User = get_user_model()
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            raise Http404()
        if user.profile:
            return user.profile
        else:
            return UserProfile(user=user, display_name=user.username)


class ProjectList(ListView):
    template_name = 'project_list.html'
    model = Project
    ordering = '-creation_time'
    paginate_by = 15


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


class ProjectLike(LoginRequiredMixin, RedirectView):
    pattern_name = 'project_details'

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        try:
            project = Project.objects.get(pk=kwargs['pk'])
        except Project.DoesNotExist:
            raise Http404()
        try:
            ProjectVote.objects.create(user=self.request.user, project=project)
        except IntegrityError:
            # double like, ignore
            pass
        return result
