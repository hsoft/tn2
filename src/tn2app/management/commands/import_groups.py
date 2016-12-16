from django.core.management.base import BaseCommand
from django.utils.html import linebreaks

from django_comments.models import Comment

from wordpress.models import WpV2BbForums, WpV2BbTopics, WpV2BbPosts, WpV2Users
from ...models import User, DiscussionGroup, Discussion
from ...util import deaccent, sanitize_comment

class Command(BaseCommand):
    help = 'Imports groups from our WP DB'

    def handle(self, *args, **options):
        wpforums = WpV2BbForums.objects
        print("Processing {} groups".format(wpforums.count()))

        # These groups end up empty at the end of the process and it's easier to blacklist them
        # excplicitly than to complicate the algo.
        EMPTY_GROUPS = {
            'couture-orientale',
            'magasins-de-tissus-a-letranger',
            'bons-plans-couture-a-hong-kong',
            'bon-plan-achat-liberty',
        }

        forumid2slug = {}
        for wpforum in wpforums.all():
            slug = deaccent(wpforum.forum_slug)
            if slug in EMPTY_GROUPS:
                continue
            forumid2slug[wpforum.forum_id] = slug
            if DiscussionGroup.objects.filter(slug=slug).exists():
                # already imported
                continue
            print(slug)
            if not WpV2BbTopics.objects.filter(forum_id=wpforum.forum_id).exists():
                print("... no topic! skipping...")
                continue
            DiscussionGroup.objects.create(
                slug=slug,
                title=wpforum.forum_name,
                description=wpforum.forum_desc,
                private=wpforum.forum_slug=='redaction',
            )

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

