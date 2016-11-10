import itertools

import bleach

def sanitize_comment(text):
    ALLOWED_TAGS = ['b', 'i', 'u', 's', 'p', 'img', 'a', 'em', 'strong', 'ul', 'ol', 'li']
    ALLOWED_ATTRS = {
        'img': ['alt', 'src', 'width', 'height'],
    }
    return bleach.linkify(bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS))

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