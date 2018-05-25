from django import template
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..models import PageContents
from ..util import gravatar_url

register = template.Library()

@register.filter(is_safe=True)
def avatar_url(user):
    if user.profile:
        if user.profile.avatar:
            return thumbnail_url(user.profile.avatar, 'avatar')
    return gravatar_url(user.email, size=34, default_image='mm')

@register.filter(is_safe=True)
def avatar_big_url(user):
    if user.profile:
        if user.profile.avatar:
            return thumbnail_url(user.profile.avatar, 'avatar-big')
    return gravatar_url(user.email, size=60, default_image='mm')

@register.filter(is_safe=True)
def avatar_bigger_url(user):
    if user.profile:
        if user.profile.avatar:
            return thumbnail_url(user.profile.avatar, 'avatar-bigger')
    return gravatar_url(user.email, size=80, default_image='mm')

@register.filter(is_safe=True)
def group_avatar_url(group):
    if group.avatar:
        return thumbnail_url(group.avatar, 'group-avatar')
    return gravatar_url(group.slug, size=80, default_image='identicon')

@register.filter(is_safe=True)
def group_avatar_big_url(group):
    if group.avatar:
        return thumbnail_url(group.avatar, 'group-avatar-big')
    return gravatar_url(group.slug, size=150, default_image='identicon')

@register.filter(is_safe=True)
def article_thumbnail(article):
    if article.main_image:
        return thumbnail_url(article.main_image, 'preview')
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

@register.filter
def thumbnail_url(source, thumb_type):
    thumbconf = settings.THUMBNAIL_ALIASES[''][thumb_type]
    size = thumbconf['size']
    url = '{}{}/{}/{}'.format(
        settings.THUMBNAIL_URL, size[0], size[1], source.name)
    return url

@register.filter
def absolute_uri(path, request):
    return request.build_absolute_uri(path)

@register.simple_tag()
def page_contents(keyname, user):
    try:
        page_contents = PageContents.objects.get(key=keyname)
        if user.has_perm('tn2app.change_pagecontents'):
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

