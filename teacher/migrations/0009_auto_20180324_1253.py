# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-24 12:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0008_auto_20180319_0710'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='change_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='publication',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
