# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-09 00:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0008_auto_20170401_2254'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='path',
        ),
    ]
