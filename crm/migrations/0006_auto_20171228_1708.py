# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-28 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_auto_20171228_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerdistribution',
            name='status',
            field=models.IntegerField(choices=[(1, '正在跟单'), (2, '已成单'), (3, '3天未跟进'), (4, '15天未成单')], default=1, verbose_name='状态'),
        ),
    ]
