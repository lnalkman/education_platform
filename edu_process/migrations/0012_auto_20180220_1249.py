# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-20 12:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu_process', '0011_message_sended'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ('-id',)},
        ),
    ]
