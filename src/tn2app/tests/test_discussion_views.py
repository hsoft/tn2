from django.core.exceptions import PermissionDenied
from django.test import TestCase, RequestFactory
from django.urls import reverse

from ..models import Discussion
from ..views import DiscussionEdit
from .factories import DiscussionFactory, DiscussionCommentFactory

class DiscussionEditTestCase(TestCase):
    def hit(self, discussion, post=None):
        kwargs={
            'group_slug': discussion.group.slug,
            'discussion_slug': discussion.slug
        }
        url = reverse('discussion_edit', kwargs=kwargs)
        if post is None:
            request = RequestFactory().get(url)
        else:
            request = RequestFactory().post(url, post)
        request.user = discussion.author
        return DiscussionEdit.as_view()(request, **kwargs)

    def test_can_delete_empty(self):
        d = DiscussionFactory.create()
        self.hit(d, post={'delete': 'yes'})
        self.assertFalse(Discussion.objects.exists())

    def test_cant_delete_discussion_with_comments(self):
        d = DiscussionFactory.create()
        DiscussionCommentFactory.create(target=d)
        with self.assertRaises(PermissionDenied):
            self.hit(d, post={'delete': 'yes'})
        self.assertTrue(Discussion.objects.exists())
