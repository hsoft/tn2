from django.test import TestCase

from .factories import DiscussionFactory, DiscussionCommentFactory

class DiscussionTestCase(TestCase):
    def test_can_delete_empty_discussion(self):
        d = DiscussionFactory.create()
        self.assertTrue(d.can_delete())

    def test_cant_delete_discussion_with_comments(self):
        d = DiscussionFactory.create()
        DiscussionCommentFactory.create(target=d)
        self.assertFalse(d.can_delete())

