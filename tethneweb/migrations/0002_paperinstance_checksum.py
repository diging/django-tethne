# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-11-16 20:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tethneweb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paperinstance',
            name='checksum',
            field=models.TextField(blank=True, null=True),
        ),
    ]