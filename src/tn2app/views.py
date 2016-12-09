from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Max
from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from django_comments.models import Comment

from .models import Article, DiscussionGroup, Discussion
from .forms import (
    NewDiscussionForm, EditDiscussionForm, NewArticleForm, EditArticleForm, EditCommentForm
)


def homepage(request):
    articles = Article.published.order_by('-creation_time')[:3]
    context = {'articles': articles}
    return render(request, 'homepage.html', context)

def article(request, slug):
    article = Article.objects.get(slug=slug)
    context = {'article': article}
    return render(request, 'article.html', context)

def discussion_groups(request):
    groups = DiscussionGroup.objects
    if not request.user.has_perm('tn2app.access_private_groups'):
        groups = groups.filter(private=False)
    groups = groups.annotate(latest_activity=Max('discussions__last_activity')).order_by('-latest_activity')
    context = {'groups': groups}
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


class UserInRedactionMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.has_perm('tn2app.add_article')


class ArticleList(ListView):
    template_name = 'article_list.html'
    model = Article
    queryset = Article.published
    ordering = '-creation_time'


class ArticleAdd(UserInRedactionMixin, CreateView):
    template_name = 'article_add.html'
    form_class = NewArticleForm

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result['author'] = self.request.user
        return result


class ArticleEdit(UserInRedactionMixin, UpdateView):
    template_name = 'article_edit.html'
    model = Article
    form_class = EditArticleForm
    context_object_name = 'article'


class CommentEdit(UserPassesTestMixin, UpdateView):
    template_name = 'comment_edit.html'
    model = Comment
    form_class = EditCommentForm
    context_object_name = 'comment'

    # for UserPassesTestMixin
    raise_exception = True

    def test_func(self):
        return self.request.user == self.get_object().user


class UserProfile(TemplateView):
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        User = get_user_model()
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            raise Http404()
        result['user'] = user
        return result
