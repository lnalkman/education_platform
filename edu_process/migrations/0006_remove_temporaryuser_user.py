# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-25 16:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu_process', '0005_auto_20171024_1418'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='temporaryuser',
            name='user',
        ),
    ]
