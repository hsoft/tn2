from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from wordpress.models import WpV2Users, WpV2Usermeta, WpV2BpXprofileData
from .models import Article, DiscussionGroup, Discussion, UserProfile

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'author', 'status', 'publish_time')
    list_filter = ('status', 'author')


admin.site.register(Article, ArticleAdmin)
admin.site.register(DiscussionGroup)
admin.site.register(Discussion)

class WPUserMetaInline(admin.TabularInline):
    model = WpV2Usermeta

class WPUserBPProfileInline(admin.TabularInline):
    model = WpV2BpXprofileData

class WPUserAdmin(admin.ModelAdmin):
    inlines = [WPUserMetaInline, WPUserBPProfileInline]
    search_fields = ['user_login', 'user_email']

admin.site.register(WpV2Users, WPUserAdmin)

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserAdminOverride(UserAdmin):
    inlines = UserAdmin.inlines + [UserProfileInline]

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdminOverride)
