# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-30 16:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0004_profile_history'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='history',
            new_name='history1',
        ),
    ]
