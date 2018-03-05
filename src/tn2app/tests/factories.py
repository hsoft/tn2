import factory
from django.contrib.auth import get_user_model

from ..models import DiscussionGroup, Discussion, DiscussionComment

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'username%d' % n)


class DiscussionGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = DiscussionGroup

    slug = factory.Sequence(lambda n: 'group%d' % n)
    title = "Some title"


class DiscussionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Discussion

    group = factory.SubFactory(DiscussionGroupFactory)
    author = factory.SubFactory(UserFactory)
    slug = factory.Sequence(lambda n: 'discussion%d' % n)
    title = "Some title"


class DiscussionCommentFactory(factory.DjangoModelFactory):
    class Meta:
        model = DiscussionComment

    target = factory.SubFactory(DiscussionFactory)
    user = factory.SubFactory(UserFactory)
