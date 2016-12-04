# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class WpV2BbForums(models.Model):
    forum_id = models.AutoField(primary_key=True)
    forum_name = models.CharField(max_length=150)
    forum_slug = models.CharField(max_length=255)
    forum_desc = models.TextField()
    forum_parent = models.IntegerField()
    forum_order = models.IntegerField()
    topics = models.BigIntegerField()
    posts = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bb_forums'


class WpV2BbMeta(models.Model):
    meta_id = models.BigAutoField(primary_key=True)
    object_type = models.CharField(max_length=16)
    object_id = models.BigIntegerField()
    meta_key = models.CharField(max_length=255, blank=True, null=True)
    meta_value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wp_v2_bb_meta'


class WpV2BbPosts(models.Model):
    post_id = models.BigAutoField(primary_key=True)
    forum_id = models.IntegerField()
    topic_id = models.BigIntegerField()
    poster_id = models.IntegerField()
    post_text = models.TextField()
    post_time = models.DateTimeField()
    poster_ip = models.CharField(max_length=15)
    post_status = models.IntegerField()
    post_position = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bb_posts'


class WpV2BbTermRelationships(models.Model):
    object_id = models.BigIntegerField()
    term_taxonomy_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    term_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bb_term_relationships'
        unique_together = (('object_id', 'term_taxonomy_id'),)


class WpV2BbTermTaxonomy(models.Model):
    term_taxonomy_id = models.BigAutoField(primary_key=True)
    term_id = models.BigIntegerField()
    taxonomy = models.CharField(max_length=32)
    description = models.TextField()
    parent = models.BigIntegerField()
    count = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bb_term_taxonomy'
        unique_together = (('term_id', 'taxonomy'),)


class WpV2BbTerms(models.Model):
    term_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=55)
    slug = models.CharField(unique=True, max_length=200)
    term_group = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bb_terms'


class WpV2BbTopics(models.Model):
    topic_id = models.BigAutoField(primary_key=True)
    topic_title = models.CharField(max_length=100)
    topic_slug = models.CharField(max_length=255)
    topic_poster = models.BigIntegerField()
    topic_poster_name = models.CharField(max_length=40)
    topic_last_poster = models.BigIntegerField()
    topic_last_poster_name = models.CharField(max_length=40)
    topic_start_time = models.DateTimeField()
    topic_time = models.DateTimeField()
    forum_id = models.IntegerField()
    topic_status = models.IntegerField()
    topic_open = models.IntegerField()
    topic_last_post_id = models.BigIntegerField()
    topic_sticky = models.IntegerField()
    topic_posts = models.BigIntegerField()
    tag_count = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bb_topics'


class WpV2BlcFilters(models.Model):
    name = models.CharField(max_length=100)
    params = models.TextField()

    class Meta:
        managed = False
        db_table = 'wp_v2_blc_filters'


class WpV2BlcInstances(models.Model):
    instance_id = models.AutoField(primary_key=True)
    link_id = models.IntegerField()
    container_id = models.IntegerField()
    container_type = models.CharField(max_length=40)
    link_text = models.CharField(max_length=250)
    parser_type = models.CharField(max_length=40)
    container_field = models.CharField(max_length=250)
    link_context = models.CharField(max_length=250)
    raw_url = models.TextField()

    class Meta:
        managed = False
        db_table = 'wp_v2_blc_instances'


class WpV2BlcLinks(models.Model):
    link_id = models.AutoField(primary_key=True)
    url = models.TextField()
    first_failure = models.DateTimeField()
    last_check = models.DateTimeField()
    last_success = models.DateTimeField()
    last_check_attempt = models.DateTimeField()
    check_count = models.IntegerField()
    final_url = models.TextField()
    redirect_count = models.SmallIntegerField()
    log = models.TextField()
    http_code = models.SmallIntegerField()
    status_code = models.CharField(max_length=100, blank=True, null=True)
    status_text = models.CharField(max_length=250, blank=True, null=True)
    request_duration = models.FloatField()
    timeout = models.IntegerField()
    broken = models.IntegerField()
    may_recheck = models.IntegerField()
    being_checked = models.IntegerField()
    result_hash = models.CharField(max_length=200)
    false_positive = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_blc_links'


class WpV2BlcSynch(models.Model):
    container_id = models.IntegerField()
    container_type = models.CharField(max_length=40)
    synched = models.IntegerField()
    last_synch = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wp_v2_blc_synch'
        unique_together = (('container_type', 'container_id'),)


class WpV2BpActivity(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    component = models.CharField(max_length=75)
    type = models.CharField(max_length=75)
    action = models.TextField()
    content = models.TextField()
    primary_link = models.CharField(max_length=150)
    item_id = models.CharField(max_length=75)
    secondary_item_id = models.CharField(max_length=75, blank=True, null=True)
    date_recorded = models.DateTimeField()
    hide_sitewide = models.IntegerField(blank=True, null=True)
    mptt_left = models.IntegerField()
    mptt_right = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_activity'


class WpV2BpActivityMeta(models.Model):
    id = models.BigAutoField(primary_key=True)
    activity_id = models.BigIntegerField()
    meta_key = models.CharField(max_length=255, blank=True, null=True)
    meta_value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_activity_meta'


class WpV2BpCoutureCategories(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_couture_categories'


class WpV2BpCoutureCommentaires(models.Model):
    id = models.BigAutoField(primary_key=True)
    item_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    content = models.TextField()
    date_posted = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_couture_commentaires'


class WpV2BpCoutureFavoris(models.Model):
    user_id = models.BigIntegerField()
    project_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_couture_favoris'
        unique_together = (('user_id', 'project_id'),)


class WpV2BpCoutureFeatured(models.Model):
    project_id = models.BigIntegerField(primary_key=True)
    date_featured = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_couture_featured'


class WpV2BpCoutureImages(models.Model):
    id = models.BigAutoField(primary_key=True)
    project_id = models.BigIntegerField()
    is_main_picture = models.IntegerField()
    img_small_url = models.CharField(max_length=250)
    img_small_dir = models.CharField(max_length=250)
    img_large_url = models.CharField(max_length=250)
    img_large_dir = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_couture_images'


class WpV2BpCoutureProjets(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    date_created = models.DateTimeField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    categorie = models.BigIntegerField(blank=True, null=True)
    patron = models.CharField(max_length=250)
    url = models.CharField(max_length=250)
    market_id = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_couture_projets'


class WpV2BpCoutureScore(models.Model):
    id_projet = models.BigIntegerField(primary_key=True)
    score = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_couture_score'


class WpV2BpCoutureVotes(models.Model):
    user_id = models.BigIntegerField()
    project_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_couture_votes'
        unique_together = (('user_id', 'project_id'),)


class WpV2BpFriends(models.Model):
    id = models.BigAutoField(primary_key=True)
    initiator_user_id = models.BigIntegerField()
    friend_user_id = models.BigIntegerField()
    is_confirmed = models.IntegerField(blank=True, null=True)
    is_limited = models.IntegerField(blank=True, null=True)
    date_created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_friends'


class WpV2BpGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    creator_id = models.BigIntegerField()
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=10)
    enable_forum = models.IntegerField()
    date_created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_groups'


class WpV2BpGroupsGroupmeta(models.Model):
    id = models.BigAutoField(primary_key=True)
    group_id = models.BigIntegerField()
    meta_key = models.CharField(max_length=255, blank=True, null=True)
    meta_value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_groups_groupmeta'


class WpV2BpGroupsMembers(models.Model):
    id = models.BigAutoField(primary_key=True)
    group_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    inviter_id = models.BigIntegerField()
    is_admin = models.IntegerField()
    is_mod = models.IntegerField()
    user_title = models.CharField(max_length=100)
    date_modified = models.DateTimeField()
    comments = models.TextField()
    is_confirmed = models.IntegerField()
    is_banned = models.IntegerField()
    invite_sent = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_groups_members'


class WpV2BpLesaviezvous(models.Model):
    texte = models.TextField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_lesaviezvous'


class WpV2BpMessagesMessages(models.Model):
    id = models.BigAutoField(primary_key=True)
    thread_id = models.BigIntegerField()
    sender_id = models.BigIntegerField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_messages_messages'


class WpV2BpMessagesNotices(models.Model):
    id = models.BigAutoField(primary_key=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField()
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_messages_notices'


class WpV2BpMessagesRecipients(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    thread_id = models.BigIntegerField()
    unread_count = models.IntegerField()
    sender_only = models.IntegerField()
    is_deleted = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_messages_recipients'


class WpV2BpNotifications(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    item_id = models.BigIntegerField()
    secondary_item_id = models.BigIntegerField(blank=True, null=True)
    component_name = models.CharField(max_length=75)
    component_action = models.CharField(max_length=75)
    date_notified = models.DateTimeField()
    is_new = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_notifications'


class WpV2BpTnSponsors(models.Model):
    id_pub = models.AutoField(primary_key=True)
    nom_pub = models.CharField(max_length=100)
    code = models.TextField()
    compteur = models.BigIntegerField()
    max = models.BigIntegerField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    zone = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_tn_sponsors'


class WpV2BpXprofileData(models.Model):
    id = models.BigAutoField(primary_key=True)
    field_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    value = models.TextField()
    last_updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_xprofile_data'


class WpV2BpXprofileFields(models.Model):
    id = models.BigAutoField(primary_key=True)
    group_id = models.BigIntegerField()
    parent_id = models.BigIntegerField()
    type = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    description = models.TextField()
    is_required = models.IntegerField()
    is_default_option = models.IntegerField()
    field_order = models.BigIntegerField()
    option_order = models.BigIntegerField()
    order_by = models.CharField(max_length=15)
    can_delete = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_xprofile_fields'


class WpV2BpXprofileGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=150)
    description = models.TextField()
    can_delete = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_bp_xprofile_groups'


class WpV2Commentmeta(models.Model):
    meta_id = models.BigAutoField(primary_key=True)
    comment_id = models.BigIntegerField()
    meta_key = models.CharField(max_length=255, blank=True, null=True)
    meta_value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wp_v2_commentmeta'


class WpV2Comments(models.Model):
    comment_id = models.BigAutoField(db_column='comment_ID', primary_key=True)  # Field name made lowercase.
    comment_post_id = models.BigIntegerField(db_column='comment_post_ID')  # Field name made lowercase.
    comment_author = models.TextField()
    comment_author_email = models.CharField(max_length=100)
    comment_author_url = models.CharField(max_length=200)
    comment_author_ip = models.CharField(db_column='comment_author_IP', max_length=100)  # Field name made lowercase.
    comment_date = models.DateTimeField()
    comment_date_gmt = models.DateTimeField()
    comment_content = models.TextField()
    comment_karma = models.IntegerField()
    comment_approved = models.CharField(max_length=20)
    comment_agent = models.CharField(max_length=255)
    comment_type = models.CharField(max_length=20)
    comment_parent = models.BigIntegerField()
    user_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_comments'


class WpV2ContactForm7(models.Model):
    cf7_unit_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    form = models.TextField()
    mail = models.TextField()
    mail_2 = models.TextField()
    messages = models.TextField()
    additional_settings = models.TextField()

    class Meta:
        managed = False
        db_table = 'wp_v2_contact_form_7'


class WpV2Gravatars(models.Model):
    email = models.CharField(unique=True, max_length=64)
    url = models.TextField()
    time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_gravatars'


class WpV2Links(models.Model):
    link_id = models.BigAutoField(primary_key=True)
    link_url = models.CharField(max_length=255)
    link_name = models.CharField(max_length=255)
    link_image = models.CharField(max_length=255)
    link_target = models.CharField(max_length=25)
    link_description = models.CharField(max_length=255)
    link_visible = models.CharField(max_length=20)
    link_owner = models.BigIntegerField()
    link_rating = models.IntegerField()
    link_updated = models.DateTimeField()
    link_rel = models.CharField(max_length=255)
    link_notes = models.TextField()
    link_rss = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'wp_v2_links'


class WpV2Options(models.Model):
    option_id = models.BigAutoField(primary_key=True)
    blog_id = models.IntegerField()
    option_name = models.CharField(unique=True, max_length=64)
    option_value = models.TextField()
    autoload = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'wp_v2_options'


#  class WpV2OtFaqCategories(models.Model):
#      id = models.AutoField(unique=True)
#      category = models.CharField(max_length=50)

#      class Meta:
#          managed = False
#          db_table = 'wp_v2_ot_faq_categories'


#  class WpV2OtFaqQuestions(models.Model):
#      id = models.AutoField(unique=True)
#      category = models.IntegerField()
#      question = models.TextField()
#      answer = models.TextField()

#      class Meta:
#          managed = False
#          db_table = 'wp_v2_ot_faq_questions'


class WpV2Postmeta(models.Model):
    meta_id = models.BigAutoField(primary_key=True)
    post_id = models.BigIntegerField()
    meta_key = models.CharField(max_length=255, blank=True, null=True)
    meta_value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wp_v2_postmeta'


class WpV2Posts(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    post_author = models.BigIntegerField()
    post_date = models.DateTimeField()
    post_date_gmt = models.DateTimeField()
    post_content = models.TextField()
    post_title = models.TextField()
    post_excerpt = models.TextField()
    post_status = models.CharField(max_length=20)
    comment_status = models.CharField(max_length=20)
    ping_status = models.CharField(max_length=20)
    post_password = models.CharField(max_length=20)
    post_name = models.CharField(max_length=200)
    to_ping = models.TextField()
    pinged = models.TextField()
    post_modified = models.DateTimeField()
    post_modified_gmt = models.DateTimeField()
    post_content_filtered = models.TextField()
    post_parent = models.BigIntegerField()
    guid = models.CharField(max_length=255)
    menu_order = models.IntegerField()
    post_type = models.CharField(max_length=20)
    post_mime_type = models.CharField(max_length=100)
    comment_count = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_posts'


class WpV2TermRelationships(models.Model):
    object_id = models.BigIntegerField()
    term_taxonomy_id = models.BigIntegerField()
    term_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_term_relationships'
        unique_together = (('object_id', 'term_taxonomy_id'),)


class WpV2TermTaxonomy(models.Model):
    term_taxonomy_id = models.BigAutoField(primary_key=True)
    term_id = models.BigIntegerField()
    taxonomy = models.CharField(max_length=32)
    description = models.TextField()
    parent = models.BigIntegerField()
    count = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_term_taxonomy'
        unique_together = (('term_id', 'taxonomy'),)


class WpV2Terms(models.Model):
    term_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    term_group = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'wp_v2_terms'


class WpV2Usermeta(models.Model):
    umeta_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(
        'WpV2Users',
        db_column='user_id',
        related_name='meta'
    )
    meta_key = models.CharField(max_length=255, blank=True, null=True)
    meta_value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wp_v2_usermeta'


class WpV2Users(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    user_login = models.CharField(unique=True, max_length=60)
    user_pass = models.CharField(max_length=64)
    user_nicename = models.CharField(max_length=50)
    user_email = models.CharField(max_length=100)
    user_url = models.CharField(max_length=100)
    user_registered = models.DateTimeField()
    user_activation_key = models.CharField(max_length=60)
    user_status = models.IntegerField()
    display_name = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'wp_v2_users'

    def __str__(self):
        return self.user_login


#  class WpV2YarppKeywordCache(models.Model):
#      id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
#      body = models.TextField()
#      title = models.TextField()
#      date = models.DateTimeField()

#      class Meta:
#          managed = False
#          db_table = 'wp_v2_yarpp_keyword_cache'


#  class WpV2YarppRelatedCache(models.Model):
#      reference_id = models.BigIntegerField(db_column='reference_ID')  # Field name made lowercase.
#      id = models.BigIntegerField(db_column='ID')  # Field name made lowercase.
#      score = models.FloatField()
#      date = models.DateTimeField()

#      class Meta:
#          managed = False
#          db_table = 'wp_v2_yarpp_related_cache'
#          unique_together = (('reference_id', 'id'),)
