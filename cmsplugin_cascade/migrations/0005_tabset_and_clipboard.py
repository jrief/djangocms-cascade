# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0004_auto_20151112_0147'),
    ]

    operations = [
        migrations.CreateModel(
            name='CascadeClipboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(unique=True, max_length=50, verbose_name='Identifier')),
                ('data', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Persited Clipboard Content',
                'verbose_name_plural': 'Persited Clipboard Content',
            },
        ),
    ]
