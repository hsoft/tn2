# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-06 03:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tn2app', '0048_articlecomment'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscussionComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submit_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('comment', models.TextField(max_length=10000)),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tn2app.Discussion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'ordering': ('submit_date',),
            },
        ),
        migrations.CreateModel(
            name='ProjectComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submit_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('comment', models.TextField(max_length=10000)),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tn2app.Project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'ordering': ('submit_date',),
            },
        ),
    ]