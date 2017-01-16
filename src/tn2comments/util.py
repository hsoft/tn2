import bleach

def sanitize_comment(text):
    ALLOWED_TAGS = ['b', 'i', 'u', 's', 'p', 'img', 'a', 'em', 'strong', 'ul', 'ol', 'li']
    ALLOWED_ATTRS = {
        'img': ['alt', 'src', 'width', 'height'],
        'a': ['href'],
    }
    return bleach.linkify(bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS))

