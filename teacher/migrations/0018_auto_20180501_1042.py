# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-01 10:42
from __future__ import unicode_literals

from django.db import migrations, models
import teacher.models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0017_course_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to=teacher.models.course_photo_path, verbose_name='Фото курсу'),
        ),
    ]
