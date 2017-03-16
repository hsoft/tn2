# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-21 03:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0003_initial_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='creation_time',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='featured',
            field=models.BooleanField(db_index=True, default=False, verbose_name='À la une'),
        ),
        migrations.AlterField(
            model_name='article',
            name='publish_time',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Brouillon'), (1, 'Révision'), (2, 'Publié')], db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='articlecategory',
            name='featured',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='discussiongroup',
            name='group_type',
            field=models.SmallIntegerField(choices=[(0, 'Thématique'), (1, 'Géographique'), (2, 'Entraide')], db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='project',
            name='creation_time',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='featured_time',
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]