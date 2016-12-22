from .util import sanitize_comment

def comment_will_be_posted(sender, comment, request, **kwargs):
    comment.comment = sanitize_comment(comment.comment)

def comment_was_posted(sender, comment, request, **kwargs):
    if hasattr(comment.content_object, 'last_activity'):
        comment.content_object.last_activity = comment.submit_date
        comment.content_object.save()
    if hasattr(comment.content_object, 'last_poster'):
        comment.content_object.last_poster = comment.user
        comment.content_object.save()

