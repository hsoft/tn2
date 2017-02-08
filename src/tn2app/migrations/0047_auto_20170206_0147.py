# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-06 01:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0046_auto_20170129_2038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='creation_time',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='is_locked',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='is_sticky',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='last_activity',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]