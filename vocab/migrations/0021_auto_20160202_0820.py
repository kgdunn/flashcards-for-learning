# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-02 08:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0020_auto_20160202_0756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(editable=False, unique=True),
        ),
    ]
