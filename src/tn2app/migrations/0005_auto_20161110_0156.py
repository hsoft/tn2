# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-10 01:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tn2app', '0004_auto_20161107_0212'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='article',
            name='creation_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.datetime_safe.datetime.now),
            preserve_default=False,
        ),
    ]
