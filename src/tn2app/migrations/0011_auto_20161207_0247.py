# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-07 02:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0010_userprofile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='city',
            field=models.TextField(blank=True, verbose_name='Ville'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='sewing_machine',
            field=models.TextField(blank=True, verbose_name='MAC'),
        ),
    ]
