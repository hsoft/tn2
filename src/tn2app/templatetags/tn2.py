from django import template
from django.templatetags.static import static
from django.utils.html import escape
from django.utils.safestring import mark_safe

from easy_thumbnails.files import get_thumbnailer

register = template.Library()

@register.filter(is_safe=True)
def avatar_url(user):
    if user.profile:
        if user.profile.avatar:
            return get_thumbnailer(user.profile.avatar)['avatar'].url
    return static('images/mystery-man-34px.jpg')

@register.filter(is_safe=True)
def avatar_big_url(user):
    if user.profile:
        if user.profile.avatar:
            return get_thumbnailer(user.profile.avatar)['avatar-big'].url
    return static('images/mystery-man-128px.jpg')

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
