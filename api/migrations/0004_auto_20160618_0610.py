# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-18 03:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_quest'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='quest',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='quest',
            name='photo',
            field=models.URLField(blank=True),
        ),
    ]
