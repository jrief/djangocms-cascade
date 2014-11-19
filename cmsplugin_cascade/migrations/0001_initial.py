# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cmsplugin_cascade.link.models
import jsonfield.fields
import cmsplugin_cascade.bootstrap3.picture
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('cms', '0004_auto_20141118_0959'),
    ]

    operations = [
        migrations.CreateModel(
            name='CascadeElement',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='+', primary_key=True, serialize=False, to='cms.CMSPlugin')),
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
                ('plugin_type', models.CharField(db_index=True, max_length=50, verbose_name='Plugin Name', choices=[(b'SimpleWrapperPlugin', b'Bootstrap Simple Wrapper')])),
                ('css_classes', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
                ('inline_styles', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
                ('site', models.ForeignKey(verbose_name='Site', to='sites.Site')),
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
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='+', primary_key=True, serialize=False, to='cms.CMSPlugin')),
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
        migrations.CreateModel(
            name='PictureElement',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(cmsplugin_cascade.bootstrap3.picture.ImagePropertyMixin, 'cmsplugin_cascade.cascadeelement'),
        ),
        migrations.CreateModel(
            name='SharableLinkElement',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(cmsplugin_cascade.link.models.LinkElementMixin, 'cmsplugin_cascade.sharablecascadeelement'),
        ),
        migrations.CreateModel(
            name='SharablePictureElement',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(cmsplugin_cascade.bootstrap3.picture.ImagePropertyMixin, cmsplugin_cascade.link.models.LinkElementMixin, 'cmsplugin_cascade.sharablecascadeelement'),
        ),
        migrations.CreateModel(
            name='SimpleLinkElement',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(cmsplugin_cascade.link.models.LinkElementMixin, 'cmsplugin_cascade.cascadeelement'),
        ),
    ]
