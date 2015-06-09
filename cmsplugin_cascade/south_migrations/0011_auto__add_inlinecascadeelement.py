# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'InlineCascadeElement'
        db.create_table(u'cmsplugin_cascade_inline', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cascade_element', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'inline_elements', to=orm['cmsplugin_cascade.CascadeElement'])),
            ('glossary', self.gf('jsonfield.fields.JSONField')(default={}, blank=True)),
        ))
        db.send_create_signal(u'cmsplugin_cascade', ['InlineCascadeElement'])


    def backwards(self, orm):
        # Deleting model 'InlineCascadeElement'
        db.delete_table(u'cmsplugin_cascade_inline')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'cmsplugin_cascade.cascadeelement': {
            'Meta': {'object_name': 'CascadeElement', 'db_table': "u'cmsplugin_cascade_element'"},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'+'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'glossary': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'})
        },
        u'cmsplugin_cascade.inlinecascadeelement': {
            'Meta': {'object_name': 'InlineCascadeElement', 'db_table': "u'cmsplugin_cascade_inline'"},
            'cascade_element': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'inline_elements'", 'to': u"orm['cmsplugin_cascade.CascadeElement']"}),
            'glossary': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'cmsplugin_cascade.pluginextrafields': {
            'Meta': {'unique_together': "((u'plugin_type', u'site'),)", 'object_name': 'PluginExtraFields'},
            'allow_id_tag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'css_classes': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_styles': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"})
        },
        u'cmsplugin_cascade.segmentation': {
            'Meta': {'object_name': 'Segmentation', 'managed': 'False'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'cmsplugin_cascade.sharablecascadeelement': {
            'Meta': {'object_name': 'SharableCascadeElement', 'db_table': "u'cmsplugin_cascade_sharableelement'"},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'+'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'glossary': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
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