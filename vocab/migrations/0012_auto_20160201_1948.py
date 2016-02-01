# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-01 19:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0011_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='slug',
            field=models.SlugField(default=''),
        ),
        migrations.AlterField(
            model_name='person',
            name='display_name',
            field=models.CharField(max_length=200, verbose_name='Display name'),
        ),
    ]
