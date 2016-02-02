# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-02 07:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0019_auto_20160201_2251'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=50)),
                ('slug', models.SlugField()),
                ('description', models.CharField(max_length=150)),
            ],
        ),
        migrations.AddField(
            model_name='worditem',
            name='tags',
            field=models.ManyToManyField(blank=True, to='vocab.Tag'),
        ),
    ]
