# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-02 18:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0014_auto_20170702_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pattern',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tn2app.PatternCreator', verbose_name='Créateur'),
        ),
    ]
