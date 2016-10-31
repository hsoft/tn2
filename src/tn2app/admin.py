from django.contrib import admin

from .models import Article, DiscussionGroup, Discussion

admin.site.register(Article)
admin.site.register(DiscussionGroup)
admin.site.register(Discussion)

