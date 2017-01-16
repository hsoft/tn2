import os
import html

from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.html import linebreaks

from django_comments.models import Comment

from wordpress.models import (
    WpV2BpGroups, WpV2BpGroupsGroupmeta, WpV2BbTopics, WpV2BbPosts, WpV2Users,
)
from tn2comments.util import sanitize_comment
from ...models import User, DiscussionGroup, Discussion
from ...util import deaccent, unescape_mysql

class Command(BaseCommand):
    help = 'Imports groups from our WP DB'

    def add_arguments(self, parser):
        parser.add_argument(
            'avatars_path',
            help="Path where WP avatars are (uploads/group-avatars)"
        )

    def handle(self, *args, **options):
        avatars_path = options['avatars_path']
        wpgroups = WpV2BpGroups.objects
        print("Processing {} groups".format(wpgroups.count()))

        # These groups end up empty at the end of the process and it's easier to blacklist them
        # excplicitly than to complicate the algo.
        EMPTY_GROUPS = {
            'couture-orientale',
        }

        forumid2slug = {}
        for wpgroup in wpgroups.all():
            slug = deaccent(wpgroup.slug)
            if slug in EMPTY_GROUPS:
                continue
            forum_id = int(WpV2BpGroupsGroupmeta.objects.get(group_id=wpgroup.id, meta_key='forum_id').meta_value)
            forumid2slug[forum_id] = slug
            if DiscussionGroup.objects.filter(slug=slug).exists():
                # already imported
                continue
            print(slug)
            if not WpV2BbTopics.objects.filter(forum_id=forum_id).exists():
                print("... no topic! skipping...")
                continue
            group = DiscussionGroup.objects.create(
                slug=slug,
                title=unescape_mysql(html.unescape(wpgroup.name)),
                description=linebreaks(unescape_mysql(sanitize_comment(wpgroup.description))),
                private=wpgroup.status=='hidden',
            )

            # Avatar
            group_path = os.path.join(avatars_path, str(wpgroup.id))
            if not os.path.exists(group_path):
                continue
            possible_matches = [fn for fn in os.listdir(group_path) if os.path.splitext(fn)[0].endswith('bpfull')]
            if possible_matches:
                to_import = possible_matches[-1]
                print("Avatar at: {}".format(to_import))
                with open(os.path.join(group_path, to_import), 'rb') as fp:
                    dfile = File(fp)
                    group.avatar.save(to_import, dfile)

        discussion2wptopic = {}
        wptopics = WpV2BbTopics.objects.filter(topic_status=0)
        for wptopic in wptopics.all():
            if wptopic.forum_id not in forumid2slug:
                continue
            group = DiscussionGroup.objects.get(slug=forumid2slug[wptopic.forum_id])
            slug = deaccent(wptopic.topic_slug)
            q = Discussion.objects.filter(group=group, slug=slug)
            if q.exists():
                # already imported
                discussion2wptopic[q.first()] = wptopic
                continue
            print(group.slug, slug)
            wpposts = WpV2BbPosts.objects.filter(
                forum_id=wptopic.forum_id, topic_id=wptopic.topic_id, post_status=0,
            ).order_by('post_time')
            if not wpposts.exists():
                print("Topic has no post! skipping...")
                continue
            first_post = wpposts.first()
            # I've tried it, and the rare occurrences where first post's author and topic's author
            # are different, it's the author from the first post that is the correct one.
            try:
                author = User.objects.get_from_wpuser_id(first_post.poster_id)
            except WpV2Users.DoesNotExist:
                print("WP user id {} doesn't exist? strange...".format(first_post.poster_id))
                continue
            discussion = Discussion.objects.create(
                group=group,
                author=author,
                slug=slug,
                title=wptopic.topic_title,
                content=linebreaks(sanitize_comment(first_post.post_text)),
                is_locked=wptopic.topic_open!=1,
                is_sticky=wptopic.topic_sticky==1,
            )
            # auto_now_add can't be overriden during create().
            discussion.creation_time=wptopic.topic_start_time
            discussion.last_activity=wptopic.topic_time
            discussion.save()
            discussion2wptopic[discussion] = wptopic

        for discussion, wptopic in discussion2wptopic.items():
            wpposts = WpV2BbPosts.objects.filter(
                forum_id=wptopic.forum_id, topic_id=wptopic.topic_id, post_status=0,
            ).order_by('post_time')
            existing_comment_count = Comment.objects.for_model(discussion).count()
            add_count = wpposts.count() - existing_comment_count - 1
            if add_count > 0:
                print("Adding {} comments to discussion {}".format(add_count, discussion.slug))
            else:
                continue
            for wppost in wpposts[existing_comment_count+1:]:
                try:
                    author = User.objects.get_from_wpuser_id(wppost.poster_id)
                except WpV2Users.DoesNotExist:
                    print("WP user id {} doesn't exist? strange...".format(wppost.poster_id))
                    continue
                Comment.objects.create(
                    content_object=discussion,
                    site_id=1,
                    user=author,
                    comment=linebreaks(sanitize_comment(wppost.post_text)),
                    submit_date=wppost.post_time,
                )

