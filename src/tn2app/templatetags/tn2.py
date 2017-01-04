from django import template
from django.templatetags.static import static
from django.utils.html import escape
from django.utils.safestring import mark_safe

from easy_thumbnails.files import get_thumbnailer

from ..models import PageContents
from ..util import gravatar_url

register = template.Library()

@register.filter(is_safe=True)
def avatar_url(user):
    if user.profile:
        if user.profile.avatar:
            return get_thumbnailer(user.profile.avatar)['avatar'].url
    return gravatar_url(user.email, size=34, default_image='mm')

@register.filter(is_safe=True)
def avatar_big_url(user):
    if user.profile:
        if user.profile.avatar:
            return get_thumbnailer(user.profile.avatar)['avatar-big'].url
    return gravatar_url(user.email, size=60, default_image='mm')

@register.filter(is_safe=True)
def group_avatar_url(group):
    if group.avatar:
        return get_thumbnailer(group.avatar)['group-avatar'].url
    return gravatar_url(group.slug, size=80, default_image='identicon')

@register.filter(is_safe=True)
def group_avatar_big_url(group):
    if group.avatar:
        return get_thumbnailer(group.avatar)['group-avatar-big'].url
    return gravatar_url(group.slug, size=150, default_image='identicon')

@register.filter(is_safe=True)
def article_thumbnail(article):
    if article.main_image:
        return get_thumbnailer(article.main_image)['preview'].url
    else:
        return static('images/image-placeholder.png')

@register.filter(is_safe=True)
def user_link(user):
    if not user:
        return ''
    elif user.profile:
        return mark_safe('<a href="{}">{}</a>'.format(
            user.profile.get_absolute_url(),
            escape(user.profile.display_name)
        ))
    else:
        return str(user)

@register.simple_tag()
def page_contents(keyname):
    try:
        return mark_safe(PageContents.objects.get(key=keyname).contents)
    except PageContents.DoesNotExist:
        return ''

