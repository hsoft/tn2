# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-05 02:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0032_auto_20180123_0226'),
    ]

    operations = [
        migrations.AddField(
            model_name='discussiongroup',
            name='ephemeral_topics',
            field=models.BooleanField(default=False),
        ),
    ]
