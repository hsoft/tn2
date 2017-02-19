# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-12 03:26
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0049_discussioncomment_projectcomment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='likes',
            field=models.ManyToManyField(related_name='liked_projects', through='tn2app.ProjectVote', to=settings.AUTH_USER_MODEL),
        ),
    ]
