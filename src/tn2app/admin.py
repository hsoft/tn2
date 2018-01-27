import datetime

from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count
from django.utils.text import slugify

from .models import (
    Article, ArticleCategory, DiscussionGroup, Discussion, UserProfile, Project, PageContents,
    PatternCreator, PatternCategory, Pattern, Sponsorship, Contest
)
from .util import dedupe_slug

class BaseModelAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/admin.css', ),
        }


class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        widgets = {
            'subtitle': forms.TextInput(),
            'categories': forms.CheckboxSelectMultiple(),
        }
        fields = (
            'title', 'subtitle', 'author', 'main_image', 'content', 'categories', 'status',
            'publish_time', 'featured',
        )

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            kwargs['initial']['author'] = self.initial_author
        super().__init__(*args, **kwargs)

    def clean(self):
        result = super().clean()
        status = self.cleaned_data.get('status')
        main_image = self.cleaned_data.get('main_image')
        if status == Article.STATUS_PUBLISHED and not main_image:
            raise ValidationError("Une image principale est nécessaire pour publier")
        return result

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.status != Article.STATUS_PUBLISHED:
            # We never change the status of a published article
            q = Article.objects.exclude(id=instance.id)
            instance.slug = dedupe_slug(slugify(instance.title), q)
        if instance.status == Article.STATUS_PUBLISHED and not instance.publish_time:
            instance.publish_time = datetime.datetime.now()
        if commit:
            instance.save()
        return instance


class ArticleAdmin(BaseModelAdmin):
    form = ArticleAdminForm
    list_display = ('slug', 'title', 'author', 'status', 'publish_time', 'featured')
    list_filter = ('status', 'featured', 'author')

    def get_form(self, request, obj=None, **kwargs):
        result = super().get_form(request, **kwargs)
        # result is a form **class**. We'll go fetch that user during __init__.
        result.initial_author = request.user
        return result


admin.site.register(Article, ArticleAdmin)

class ArticleCategoryAdmin(BaseModelAdmin):
    list_display = ('slug', 'title', 'featured')
    list_filter = ('featured', )


admin.site.register(ArticleCategory, ArticleCategoryAdmin)

class DiscussionGroupAdmin(BaseModelAdmin):
    list_display = ('slug', 'title', 'group_type', 'private')
    list_filter = ('group_type', 'private')

admin.site.register(DiscussionGroup, DiscussionGroupAdmin)

class DiscussionAdmin(BaseModelAdmin):
    list_display = ('slug', 'title', 'group', 'creation_time', 'last_activity')
    list_filter = ('group', )


admin.site.register(Discussion, DiscussionAdmin)

class ProjectAdmin(BaseModelAdmin):
    readonly_fields = ('author', )
    exclude = ('featured_time', 'creation_time')


admin.site.register(Project, ProjectAdmin)

admin.site.register(PageContents, BaseModelAdmin)
admin.site.register(PatternCreator, BaseModelAdmin)
admin.site.register(PatternCategory, BaseModelAdmin)

class PatternAdmin(BaseModelAdmin):
    list_display = ('name', 'creator', 'target', 'domain', 'category', 'is_free', 'is_jersey')
    list_filter = ('creator', 'target', 'domain', 'category', 'is_free', 'is_jersey')
    search_fields = ('name',)
    save_as = True

admin.site.register(Pattern, PatternAdmin)

class ContestAdmin(BaseModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput},
    }
    list_display = ('name', 'active')
    list_filter = ('active', )

admin.site.register(Contest, ContestAdmin)

admin.site.register(Sponsorship, BaseModelAdmin)

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserAdminOverride(UserAdmin):
    inlines = UserAdmin.inlines + [UserProfileInline]
    list_display = (
        'username', 'email', 'is_staff', 'last_login', 'date_joined', 'project_count',
        'like_count')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(project_count=Count('projects', distinct=True)) \
            .annotate(like_count=Count('projects__likes', distinct=True))

    def project_count(self, obj):
        return obj.project_count

    project_count.short_description = "Projets"
    project_count.admin_order_field = 'project_count'

    def like_count(self, obj):
        return obj.like_count

    like_count.short_description = "Likes"
    like_count.admin_order_field = 'like_count'

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdminOverride)
