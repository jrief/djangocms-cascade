# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PluginExtraFields'
        db.create_table(u'cmsplugin_cascade_pluginextrafields', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plugin_type', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('css_classes', self.gf('jsonfield.fields.JSONField')(default={}, null=True, blank=True)),
            ('inline_styles', self.gf('jsonfield.fields.JSONField')(default={}, null=True, blank=True)),
        ))
        db.send_create_signal('cmsplugin_cascade', ['PluginExtraFields'])


    def backwards(self, orm):
        # Deleting model 'PluginExtraFields'
        db.delete_table(u'cmsplugin_cascade_pluginextrafields')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'cmsplugin_cascade.cascadeelement': {
            'Meta': {'object_name': 'CascadeElement', 'db_table': "'cmsplugin_cascade_element'"},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'+'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'glossary': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'})
        },
        'cmsplugin_cascade.pluginextrafields': {
            'Meta': {'object_name': 'PluginExtraFields'},
            'css_classes': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_styles': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"})
        },
        u'cmsplugin_cascade.sharablecascadeelement': {
            'Meta': {'object_name': 'SharableCascadeElement', 'db_table': "u'cmsplugin_cascade_sharableelement'"},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'+'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'glossary': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            'shared_glossary': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cmsplugin_cascade.SharedGlossary']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'cmsplugin_cascade.sharedglossary': {
            'Meta': {'unique_together': "((u'plugin_type', u'identifier'),)", 'object_name': 'SharedGlossary'},
            'glossary': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['cmsplugin_cascade']