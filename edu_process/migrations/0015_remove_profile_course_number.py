# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-15 16:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu_process', '0014_auto_20180220_1251'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='course_number',
        ),
    ]
