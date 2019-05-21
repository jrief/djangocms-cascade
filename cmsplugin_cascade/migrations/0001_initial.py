# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import cmsplugin_cascade.mixins
import cmsplugin_cascade.link.plugin_base
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('cms', '0003_auto_20140926_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='CascadeElement',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='+', primary_key=True, serialize=False, to='cms.CMSPlugin', on_delete=models.CASCADE)),
                ('glossary', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
            ],
            options={
                'db_table': 'cmsplugin_cascade_element',
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='PluginExtraFields',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('plugin_type', models.CharField(db_index=True, max_length=50, verbose_name='Plugin Name', choices=[(b'BootstrapButtonPlugin', b'Bootstrap Button'), (b'SimpleWrapperPlugin', b'Bootstrap Simple Wrapper'), (b'BootstrapRowPlugin', b'Bootstrap Row'), (b'BootstrapPicturePlugin', b'Bootstrap Picture'), (b'BootstrapContainerPlugin', b'Bootstrap Container'), (b'BootstrapColumnPlugin', b'Bootstrap Column')])),
                ('allow_id_tag', models.BooleanField(default=False)),
                ('css_classes', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
                ('inline_styles', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
                ('site', models.ForeignKey(verbose_name='Site', to='sites.Site', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Custom CSS classes and styles',
                'verbose_name_plural': 'Custom CSS classes and styles',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SharableCascadeElement',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='+', primary_key=True, serialize=False, to='cms.CMSPlugin', on_delete=models.CASCADE)),
                ('glossary', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
            ],
            options={
                'db_table': 'cmsplugin_cascade_sharableelement',
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='SharedGlossary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('plugin_type', models.CharField(verbose_name='Plugin Name', max_length=50, editable=False, db_index=True)),
                ('identifier', models.CharField(unique=True, max_length=50, verbose_name='Identifier')),
                ('glossary', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Shared between Plugins',
                'verbose_name_plural': 'Shared between Plugins',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sharedglossary',
            unique_together=set([('plugin_type', 'identifier')]),
        ),
        migrations.AddField(
            model_name='sharablecascadeelement',
            name='shared_glossary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='cmsplugin_cascade.SharedGlossary', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='pluginextrafields',
            unique_together=set([('plugin_type', 'site')]),
        ),
    ]
