# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-23 19:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0003_auto_20160123_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='worditem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vocab.WordItem'),
        ),
    ]
