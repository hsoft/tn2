from django.shortcuts import render

from .models import Article

def homepage(request):
    articles = Article.objects.all()
    context = {'articles': articles}
    return render(request, 'homepage.html', context)

def article(request, slug):
    article = Article.objects.get(slug=slug)
    context = {'article': article}
    return render(request, 'article.html', context)

