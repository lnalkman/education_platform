# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-01 13:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0010_auto_20180324_1952'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='markdown',
        ),
        migrations.AddField(
            model_name='publication',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Фотокартка публікації'),
        ),
    ]
