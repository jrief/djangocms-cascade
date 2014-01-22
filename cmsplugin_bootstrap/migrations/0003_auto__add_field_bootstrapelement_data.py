# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'BootstrapElement.extra_classes'
        db.delete_column(u'cmsplugin_bootstrapelement', 'extra_classes')

        # Deleting field 'BootstrapElement.class_name'
        db.delete_column(u'cmsplugin_bootstrapelement', 'class_name')

        # Deleting field 'BootstrapElement.tagged_classes'
        db.delete_column(u'cmsplugin_bootstrapelement', 'tagged_classes')

        # Deleting field 'BootstrapElement.options'
        db.delete_column(u'cmsplugin_bootstrapelement', 'options')

        # Deleting field 'BootstrapElement.extra_styles'
        db.delete_column(u'cmsplugin_bootstrapelement', 'extra_styles')

        # Deleting field 'BootstrapElement.tag_type'
        db.delete_column(u'cmsplugin_bootstrapelement', 'tag_type')

        # Adding field 'BootstrapElement.data'
        db.add_column(u'cmsplugin_bootstrapelement', 'data',
                      self.gf('jsonfield.fields.JSONField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'BootstrapElement.extra_classes'
        db.add_column(u'cmsplugin_bootstrapelement', 'extra_classes',
                      self.gf('jsonfield.fields.JSONField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BootstrapElement.class_name'
        db.add_column(u'cmsplugin_bootstrapelement', 'class_name',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'BootstrapElement.tagged_classes'
        db.add_column(u'cmsplugin_bootstrapelement', 'tagged_classes',
                      self.gf('jsonfield.fields.JSONField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BootstrapElement.options'
        db.add_column(u'cmsplugin_bootstrapelement', 'options',
                      self.gf('jsonfield.fields.JSONField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BootstrapElement.extra_styles'
        db.add_column(u'cmsplugin_bootstrapelement', 'extra_styles',
                      self.gf('jsonfield.fields.JSONField')(null=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'BootstrapElement.tag_type'
        raise RuntimeError("Cannot reverse this migration. 'BootstrapElement.tag_type' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'BootstrapElement.tag_type'
        db.add_column(u'cmsplugin_bootstrapelement', 'tag_type',
                      self.gf('django.db.models.fields.CharField')(max_length=50),
                      keep_default=False)

        # Deleting field 'BootstrapElement.data'
        db.delete_column(u'cmsplugin_bootstrapelement', 'data')


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
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'+'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['cmsplugin_bootstrap']