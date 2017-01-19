import hashlib
import itertools
import re
import unicodedata

from django.utils.html import format_html

def dedupe_slug(slug, queryset, slug_field_name='slug'):
    model = queryset.model
    max_length = model._meta.get_field(slug_field_name).max_length
    # Never going to be above 1000 conflicts...
    slug = slug_orig = slug[:max_length-4]
    for i in itertools.count(1):
        if queryset.filter(**{slug_field_name: slug}).exists():
            slug = "{}-{}".format(slug_orig, i)
        else:
            return slug

def nonone(value, replace_value):
    """Returns ``value`` if ``value`` is not ``None``. Returns ``replace_value`` otherwise.
    """
    if value is None:
        return replace_value
    else:
        return value

def deaccent(s):
    # http://stackoverflow.com/a/15261831
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def unescape_mysql(s):
    return s.replace('\\\'', '\'').replace('\\"', '"')

def gravatar_url(email, size=None, default_image=None):
    normalized = email.strip().lower()
    email_hash = hashlib.md5(normalized.encode('utf-8')).hexdigest()
    url = 'https://www.gravatar.com/avatar/{}.jpg'.format(email_hash)
    params = {}
    if size:
        params['s'] = str(size)
    if default_image:
        params['d'] = default_image
    if params:
        url += '?' + '&'.join('{}={}'.format(k, v) for k, v in params.items())
    return url

def fa_str(fa_name):
    return format_html('<span class="fa fa-{}"></span>', fa_name)

def embed_videos(html, width=630):
    """Replaces youtube and vimeo links by proper embed iframes
    """
    def youtuberepl(match):
        youtube_id = match.group(1)
        HEIGHT_RATIO = 380 / 630
        height = width * HEIGHT_RATIO
        return '<iframe width="{width:.0f}" height="{height:.0f}" src="https://www.youtube.com/embed/{id}" frameborder="0" allowfullscreen></iframe>'.format(
            width=width,
            height=height,
            id=youtube_id
        )

    html = re.sub(
        r'(?!")(?<!")(?:\[youtube[^]]*\])?https?://www\.youtube\.com/watch\?v=([\w\-]+)(?:\[/youtube\])?',
        youtuberepl,
        html
    )
    html = re.sub(
        r'\[youtube[^]]*\]([\w\-]+)\[/youtube\]',
        youtuberepl,
        html
    )

    def vimeorepl(match):
        vimeo_id = match.group(1)
        HEIGHT_RATIO = 354 / 630
        height = width * HEIGHT_RATIO
        return '<iframe src="https://player.vimeo.com/video/{id}" width="{width:.0f}" height="{height:.0f}" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>'.format(
            width=width,
            height=height,
            id=vimeo_id
        )

    html = re.sub(
        r'(?!")(?<!")(?:\[vimeo[^]]*\])?https?://vimeo\.com/(\d+)(?:\[/vimeo\])?',
        vimeorepl,
        html
    )
    return html

