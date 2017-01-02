# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-31 21:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0032_auto_20161231_0118'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX tn2app_project_ts1_idx ON tn2app_project USING gin(to_tsvector('french', coalesce(title, '') || ' ' || coalesce(description, '') || ' ' || coalesce(pattern_name, '')));",
            "DROP INDEX IF EXISTS tn2app_project_ts1_idx;"
        ),
    ]