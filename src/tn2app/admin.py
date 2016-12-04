from django.contrib import admin

from wordpress.models import WpV2Users, WpV2Usermeta
from .models import Article, DiscussionGroup, Discussion

admin.site.register(Article)
admin.site.register(DiscussionGroup)
admin.site.register(Discussion)

class WPUserMetaInline(admin.TabularInline):
    model = WpV2Usermeta

class WPUserAdmin(admin.ModelAdmin):
    inlines = [WPUserMetaInline]

admin.site.register(WpV2Users, WPUserAdmin)
