# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BootstrapElement'
        db.create_table(u'cmsplugin_bootstrapelement', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(related_name='+', unique=True, primary_key=True, to=orm['cms.CMSPlugin'])),
            ('tag_type', self.gf('django.db.models.fields.CharField')(default='naked', max_length=50)),
            ('class_name', self.gf('django.db.models.fields.CharField')(default='btn', max_length=50, null=True, blank=True)),
            ('extra_classes', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('extra_styles', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'cmsplugin_bootstrap', ['BootstrapElement'])


    def backwards(self, orm):
        # Deleting model 'BootstrapElement'
        db.delete_table(u'cmsplugin_bootstrapelement')


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
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'cmsplugin_bootstrap.bootstrapelement': {
            'Meta': {'object_name': 'BootstrapElement', 'db_table': "u'cmsplugin_bootstrapelement'", '_ormbases': ['cms.CMSPlugin']},
            'class_name': ('django.db.models.fields.CharField', [], {'default': "'btn'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'+'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'extra_classes': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'extra_styles': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'tag_type': ('django.db.models.fields.CharField', [], {'default': "'naked'", 'max_length': '50'})
        }
    }

    complete_apps = ['cmsplugin_bootstrap']