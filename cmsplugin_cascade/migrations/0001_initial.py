# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0007_auto_20141028_1559'),
    ]

    operations = [
        migrations.CreateModel(
            name='CascadeElement',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='+', primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('glossary', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
            ],
            options={
            },
            bases=('cms.cmsplugin',),
        ),
    ]
