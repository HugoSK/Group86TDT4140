# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-21 08:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0010_auto_20170421_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slowdown',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 21, 8, 34, 57, 956422)),
        ),
    ]