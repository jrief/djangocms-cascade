# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0006_bootstrapgallerypluginmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeadingPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='HorizontalRulePluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='SegmentPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='SimpleWrapperPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
    ]
