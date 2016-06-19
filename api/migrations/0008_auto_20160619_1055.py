# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-19 07:55
from __future__ import unicode_literals

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20160619_0220'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=api.models.upload_to)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='quest',
            name='photo',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='api.File'),
        ),
        migrations.AlterField(
            model_name='question',
            name='photo',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='api.File'),
        ),
    ]