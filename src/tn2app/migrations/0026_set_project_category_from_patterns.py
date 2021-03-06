# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-10 00:52
from __future__ import unicode_literals

from django.db import migrations


def set_project_category_from_patterns(apps, schema_editor):
    Project = apps.get_model('tn2app', 'Project')
    for p in Project.objects.filter(pattern__isnull=False):
        p.target = p.pattern.target
        p.domain = p.pattern.domain
        p.category_id = p.pattern.category_id
        p.save()

class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0025_auto_20170710_0043'),
    ]

    operations = [
        migrations.RunPython(set_project_category_from_patterns),
    ]
