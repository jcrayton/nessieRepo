# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-01 13:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calender', '0005_auto_20170131_0558'),
    ]

    operations = [
        migrations.AddField(
            model_name='calender',
            name='event_google_id',
            field=models.CharField(default='', max_length=40),
            preserve_default=False,
        ),
    ]
