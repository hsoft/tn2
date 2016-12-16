# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-13 02:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0015_auto_20161209_0256'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('featured', models.BooleanField(default=False)),
            ],
        ),
    ]