# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Style.padding_left'
        db.add_column('cmsplugin_style', 'padding_left',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Style.padding_right'
        db.add_column('cmsplugin_style', 'padding_right',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Style.padding_top'
        db.add_column('cmsplugin_style', 'padding_top',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Style.padding_bottom'
        db.add_column('cmsplugin_style', 'padding_bottom',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Style.margin_left'
        db.add_column('cmsplugin_style', 'margin_left',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Style.margin_right'
        db.add_column('cmsplugin_style', 'margin_right',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Style.margin_top'
        db.add_column('cmsplugin_style', 'margin_top',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Style.margin_bottom'
        db.add_column('cmsplugin_style', 'margin_bottom',
                      self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True),
                      keep_default=False)


        # Changing field 'Style.class_name'
        db.alter_column('cmsplugin_style', 'class_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

    def backwards(self, orm):
        # Deleting field 'Style.padding_left'
        db.delete_column('cmsplugin_style', 'padding_left')

        # Deleting field 'Style.padding_right'
        db.delete_column('cmsplugin_style', 'padding_right')

        # Deleting field 'Style.padding_top'
        db.delete_column('cmsplugin_style', 'padding_top')

        # Deleting field 'Style.padding_bottom'
        db.delete_column('cmsplugin_style', 'padding_bottom')

        # Deleting field 'Style.margin_left'
        db.delete_column('cmsplugin_style', 'margin_left')

        # Deleting field 'Style.margin_right'
        db.delete_column('cmsplugin_style', 'margin_right')

        # Deleting field 'Style.margin_top'
        db.delete_column('cmsplugin_style', 'margin_top')

        # Deleting field 'Style.margin_bottom'
        db.delete_column('cmsplugin_style', 'margin_bottom')


        # Changing field 'Style.class_name'
        db.alter_column('cmsplugin_style', 'class_name', self.gf('django.db.models.fields.CharField')(max_length=50))

    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 12, 13, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'djangocms_style.style': {
            'Meta': {'object_name': 'Style', 'db_table': "'cmsplugin_style'", '_ormbases': ['cms.CMSPlugin']},
            'class_name': ('django.db.models.fields.CharField', [], {'default': "'info'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'margin_bottom': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'margin_left': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'margin_right': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'margin_top': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'padding_bottom': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'padding_left': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'padding_right': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'padding_top': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['djangocms_style']