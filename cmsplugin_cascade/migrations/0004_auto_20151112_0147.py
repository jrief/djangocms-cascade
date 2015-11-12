# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0003_inlinecascadeelement'),
    ]

    operations = [
        migrations.DeleteModel(
            name='HorizontalRulePluginModel',
        ),
        migrations.DeleteModel(
            name='PanelGroupPluginModel',
        ),
        migrations.DeleteModel(
            name='PanelPluginModel',
        ),
        migrations.DeleteModel(
            name='SimpleWrapperPluginModel',
        ),
        migrations.CreateModel(
            name='BootstrapAccordionPanelPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='BootstrapAccordionPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='BootstrapPanelPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='BootstrapSecondaryMenuPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
    ]
