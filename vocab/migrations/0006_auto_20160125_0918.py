# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-25 09:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0005_quiz_when_last_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='n_words_asked',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='quiz_hash',
            field=models.TextField(max_length=8, unique=True),
        ),
    ]
