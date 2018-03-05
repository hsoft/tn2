from django.test import TestCase

from .factories import (
    DiscussionFactory, DiscussionCommentFactory, DiscussionGroupFactory
)

class DiscussionTestCase(TestCase):
    def test_can_delete_empty_discussion(self):
        d = DiscussionFactory.create()
        self.assertTrue(d.can_delete())

    def test_cant_delete_discussion_with_comments(self):
        d = DiscussionFactory.create()
        DiscussionCommentFactory.create(target=d)
        self.assertFalse(d.can_delete())

    def test_can_always_delete_group_ephemeral_groups(self):
        g = DiscussionGroupFactory.create(ephemeral_topics=True)
        d = DiscussionFactory.create(group=g)
        DiscussionCommentFactory.create(target=d)
        self.assertTrue(d.can_delete())
