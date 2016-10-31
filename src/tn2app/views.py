from django.shortcuts import render

from .models import Article, DiscussionGroup, Discussion

def homepage(request):
    articles = Article.objects.all()
    context = {'articles': articles}
    return render(request, 'homepage.html', context)

def article(request, slug):
    article = Article.objects.get(slug=slug)
    context = {'article': article}
    return render(request, 'article.html', context)

def discussion_groups(request):
    groups = DiscussionGroup.objects
    print(repr(request.user.is_staff))
    if not request.user.is_staff:
        groups = groups.filter(private=False)
    context = {'groups': groups.all()}
    return render(request, 'discussion_groups.html', context)

def discussion_group(request, group_slug):
    group = DiscussionGroup.objects.get(slug=group_slug)
    context = {'group': group}
    return render(request, 'discussion_group.html', context)

def discussion(request, group_slug, discussion_slug):
    discussion = Discussion.objects.get(group__slug=group_slug, slug=discussion_slug)
    context = {'discussion': discussion}
    return render(request, 'discussion.html', context)
