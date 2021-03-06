# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-06 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0018_auto_20170705_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pattern',
            name='domain',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Couture'), (2, 'Tricot'), (3, 'Crochet'), (4, 'Broderie')], db_index=True, verbose_name='Domaine'),
        ),
        migrations.AlterField(
            model_name='pattern',
            name='target',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Femme'), (2, 'Homme'), (3, 'Enfant'), (4, 'Accessoire')], db_index=True, verbose_name='Destinataire'),
        ),
    ]
