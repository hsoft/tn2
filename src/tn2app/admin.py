from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django import forms

from wordpress.models import WpV2Users, WpV2Usermeta, WpV2BpXprofileData
from .models import (
    Article, ArticleCategory, DiscussionGroup, Discussion, UserProfile, Project, PageContents
)

class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        widgets = {
            'subtitle': forms.TextInput(),
        }
        fields = ('slug', 'title', 'subtitle', 'author', 'content', 'status', 'publish_time', 'featured')


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('slug', 'title', 'author', 'status', 'publish_time', 'featured')
    list_filter = ('status', 'featured', 'author')
    readonly_fields = ('author', )


admin.site.register(Article, ArticleAdmin)

class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'featured')
    list_filter = ('featured', )


admin.site.register(ArticleCategory, ArticleCategoryAdmin)

class DiscussionGroupAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'group_type', 'private')
    list_filter = ('group_type', 'private')

admin.site.register(DiscussionGroup, DiscussionGroupAdmin)

class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'group', 'creation_time', 'last_activity')
    list_filter = ('group', )

admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Project)
admin.site.register(PageContents)

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
