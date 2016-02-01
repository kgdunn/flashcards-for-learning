# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-01 22:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0016_quiz_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizworditem',
            name='person',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, to='vocab.Person'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocab.Person'),
        ),
    ]
