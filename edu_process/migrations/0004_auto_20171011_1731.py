# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-11 14:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu_process', '0003_auto_20171011_0024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='author',
        ),
        migrations.RemoveField(
            model_name='course',
            name='visible_for_groups',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='module',
        ),
        migrations.RemoveField(
            model_name='lessonfile',
            name='lesson',
        ),
        migrations.RemoveField(
            model_name='module',
            name='course',
        ),
        migrations.DeleteModel(
            name='Course',
        ),
        migrations.DeleteModel(
            name='Lesson',
        ),
        migrations.DeleteModel(
            name='LessonFile',
        ),
        migrations.DeleteModel(
            name='Module',
        ),
    ]
