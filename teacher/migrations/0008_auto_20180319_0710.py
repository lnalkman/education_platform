# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-19 07:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0007_auto_20171121_1055'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='module',
            options={'verbose_name': 'Розділ', 'verbose_name_plural': 'Розділи'},
        ),
        migrations.AlterField(
            model_name='module',
            name='description',
            field=models.TextField(max_length=4096, verbose_name='Опис розділу'),
        ),
        migrations.AlterField(
            model_name='module',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Назва розділу'),
        ),
    ]