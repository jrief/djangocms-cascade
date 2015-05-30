# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Segmentation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'Segmentation',
                'managed': False,
                'verbose_name_plural': 'Segmentation',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='cascadeelement',
            name='glossary',
            field=jsonfield.fields.JSONField(default={}, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pluginextrafields',
            name='plugin_type',
            field=models.CharField(max_length=50, verbose_name='Plugin Name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sharablecascadeelement',
            name='glossary',
            field=jsonfield.fields.JSONField(default={}, blank=True),
            preserve_default=True,
        ),
    ]
