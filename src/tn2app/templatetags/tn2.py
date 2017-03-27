from django import template
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html
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
def avatar_bigger_url(user):
    if user.profile:
        if user.profile.avatar:
            return get_thumbnailer(user.profile.avatar)['avatar-bigger'].url
    return gravatar_url(user.email, size=80, default_image='mm')

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
        return user.profile.link()
    else:
        return str(user)

@register.filter
def fixurl(url):
    if not url:
        return url
    if not url.startswith('http'):
        url = 'http://{}'.format(url)
    return url

@register.simple_tag()
def page_contents(keyname, user):
    try:
        page_contents = PageContents.objects.get(key=keyname)
        if user.is_staff:
            edit_link = reverse('admin:tn2app_pagecontents_change', args=(page_contents.id, ))
            return format_html(
                '<a class="page-edit-link" href="{}"><span class="fa fa-edit"></span></a>{}',
                edit_link,
                mark_safe(page_contents.contents),
            )
        else:
            return mark_safe(page_contents.contents)
    except PageContents.DoesNotExist:
        return ''

