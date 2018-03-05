import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from ..models import DiscussionGroup, Discussion, DiscussionComment

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'username%d' % n)

    @factory.post_generation
    def moderator(obj, created, extracted, **kwargs):
        if extracted:
            content_type = ContentType.objects.get_for_model(Discussion)
            permission = Permission.objects.get(
                content_type=content_type,
                codename='change_discussion')
            obj.user_permissions.add(permission)


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
