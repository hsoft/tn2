# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-20 02:37
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0024_project_legacy_like_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=ckeditor.fields.RichTextField(),
        ),
    ]