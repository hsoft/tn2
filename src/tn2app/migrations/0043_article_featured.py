# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-15 18:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0042_article_subtitle'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='featured',
            field=models.BooleanField(default=False, verbose_name='À la une'),
        ),
    ]