# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-31 10:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0008_auto_20180831_1239'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Result',
        ),
        migrations.DeleteModel(
            name='Search',
        ),
    ]
