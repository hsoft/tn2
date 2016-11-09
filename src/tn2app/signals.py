from .util import sanitize_comment

def comment_will_be_posted(sender, comment, request, **kwargs):
    comment.comment = sanitize_comment(comment.comment)

