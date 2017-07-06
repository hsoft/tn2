# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-02 18:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tn2app', '0013_auto_20170701_1954'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatternCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Catégorie de patrons',
                'verbose_name_plural': 'Catégories de patrons',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='pattern',
            name='domain',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Couture'), (2, 'Tricot'), (3, 'Crochet'), (4, 'Broderie'), (0, 'Aucun')], db_index=True, default=0, verbose_name='Domaine'),
        ),
        migrations.AddField(
            model_name='pattern',
            name='target',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Femme'), (2, 'Homme'), (3, 'Enfant'), (4, 'Accessoire'), (0, 'Aucun')], db_index=True, default=0, verbose_name='Destinataire'),
        ),
        migrations.AddField(
            model_name='pattern',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tn2app.PatternCategory', verbose_name='Categorie'),
        ),
    ]