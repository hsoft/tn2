from functools import partial
import hashlib
import itertools
import re
import unicodedata

from bleach.callbacks import nofollow, target_blank
from bleach.linkifier import LinkifyFilter
from bleach.sanitizer import Cleaner
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.validators import URLValidator
from django.db.models.fields import URLField
from django.utils.html import format_html
from PIL import Image

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

def href(url, label, newwindow=False):
    if newwindow:
        fmt = '<a href="{}" target="_blank">{}</a>'
    else:
        fmt = '<a href="{}">{}</a>'
    return format_html(fmt, url, label)

def embed_videos(html, width=630, strip=False):
    """Replaces youtube and vimeo links by proper embed iframes
    """
    def youtuberepl(match):
        if strip:
            return ''
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
        if strip:
            return ''
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

def sanitize_comment(text):
    ALLOWED_TAGS = ['b', 'i', 'u', 's', 'p', 'br', 'img', 'a', 'em', 'strong', 'ul', 'ol', 'li']
    ALLOWED_ATTRS = {
        'img': ['alt', 'src', 'width', 'height'],
        'a': ['href'],
    }
    cleaner = Cleaner(
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        filters=[partial(LinkifyFilter, callbacks=[nofollow, target_blank])]
    )
    return cleaner.clean(text)

def extract_media_paths(html_content):
    """Returns a list of media paths references in `html_content`.

    Those paths are relative to MEDIA_ROOT.
    """
    soup = BeautifulSoup(html_content)
    for img in soup.find_all('img'):
        src = img['src']
        if src.startswith(settings.MEDIA_URL):
            yield src[len(settings.MEDIA_URL):]

# https://github.com/SmileyChris/easy-thumbnails/blob/master/easy_thumbnails/utils.py#L111
def exif_orientation(im):
    try:
        exif = im._getexif()
    except Exception:
        # There are many ways that _getexif fails, we're just going to blanket
        # cover them all.
        return im
    if exif is None:
        return im
    orientation = exif.get(0x0112)
    if orientation == 2:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 3:
        im = im.transpose(Image.ROTATE_180)
    elif orientation == 4:
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
    elif orientation == 5:
        im = im.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 6:
        im = im.transpose(Image.ROTATE_270)
    elif orientation == 7:
        im = im.transpose(Image.ROTATE_90).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 8:
        im = im.transpose(Image.ROTATE_90)
    return im

# Low-tech approach to work around the too strict URLValidator.
# Context: https://code.djangoproject.com/ticket/20264
# replace() isn't super elegant, but I prefer this to having to copy/paste the whole big regexp
# soup from URLValidator so that I can add one underscore...
class PermissiveURLValidator(URLValidator):
    def __call__(self, value):
        value = value.replace('_', '-')
        return super().__call__(value)


class PermissiveURLField(URLField):
    default_validators = [PermissiveURLValidator()]

    def formfield(self, **kwargs):
        result = super().formfield(**kwargs)
        result.validators = [PermissiveURLValidator()]
        return result

