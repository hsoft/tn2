from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.generic.edit import CreateView

from .models import Article, DiscussionGroup, Discussion
from .forms import NewDiscussionForm, NewArticleForm

def homepage(request):
    articles = Article.objects.all().order_by('-creation_time')
    context = {'articles': articles}
    return render(request, 'homepage.html', context)

def article(request, slug):
    article = Article.objects.get(slug=slug)
    context = {'article': article}
    return render(request, 'article.html', context)

def discussion_groups(request):
    groups = DiscussionGroup.objects
    if not request.user.is_staff:
        groups = groups.filter(private=False)
    context = {'groups': groups.all()}
    return render(request, 'discussion_groups.html', context)

def discussion_group(request, group_slug):
    group = DiscussionGroup.objects.get(slug=group_slug)
    if group.private and not request.user.is_staff:
        raise PermissionDenied()
    context = {'group': group}
    return render(request, 'discussion_group.html', context)

def discussion(request, group_slug, discussion_slug):
    discussion = Discussion.objects.get(group__slug=group_slug, slug=discussion_slug)
    if discussion.group.private and not request.user.is_staff:
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

class ArticleAdd(UserPassesTestMixin, CreateView):
    template_name = 'article_add.html'
    form_class = NewArticleForm

    def test_func(self):
        return self.request.user.has_perm('tn2app.add_article')

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result['author'] = self.request.user
        return result
