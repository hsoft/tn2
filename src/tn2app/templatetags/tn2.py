from django import template
from django.templatetags.static import static

from easy_thumbnails.files import get_thumbnailer

register = template.Library()

@register.filter(is_safe=True)
def avatar_url(user):
    if user.profile:
        if user.profile.avatar:
            return get_thumbnailer(user.profile.avatar)['avatar'].url
    return static('images/mystery-man-34px.jpg')

