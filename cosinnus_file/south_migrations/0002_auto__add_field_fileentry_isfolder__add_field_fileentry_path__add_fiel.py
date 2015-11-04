# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'FileEntry', fields ['group', 'slug']
        db.delete_unique(u'cosinnus_file_fileentry', ['group_id', 'slug'])

        # Adding field 'FileEntry.isfolder'
        db.add_column(u'cosinnus_file_fileentry', 'isfolder',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'FileEntry.path'
        db.add_column(u'cosinnus_file_fileentry', 'path',
                      self.gf('django.db.models.fields.CharField')(default=u'/', max_length=100),
                      keep_default=False)

        # Adding field 'FileEntry._sourcefilename'
        db.add_column(u'cosinnus_file_fileentry', '_sourcefilename',
                      self.gf('django.db.models.fields.CharField')(default=u'download', max_length=100),
                      keep_default=False)


        # Changing field 'FileEntry.group'
        db.alter_column(u'cosinnus_file_fileentry', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['cosinnus.CosinnusGroup']))

    def backwards(self, orm):
        # Deleting field 'FileEntry.isfolder'
        db.delete_column(u'cosinnus_file_fileentry', 'isfolder')

        # Deleting field 'FileEntry.path'
        db.delete_column(u'cosinnus_file_fileentry', 'path')

        # Deleting field 'FileEntry._sourcefilename'
        db.delete_column(u'cosinnus_file_fileentry', '_sourcefilename')


        # Changing field 'FileEntry.group'
        db.alter_column(u'cosinnus_file_fileentry', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['auth.Group']))
        # Adding unique constraint on 'FileEntry', fields ['group', 'slug']
        db.create_unique(u'cosinnus_file_fileentry', ['group_id', 'slug'])


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'cosinnus.cosinnusgroup': {
            'Meta': {'object_name': 'CosinnusGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'cosinnus_groups'", 'symmetrical': 'False', 'to': u"orm['auth.User']"})
        },
        u'cosinnus.tagobject': {
            'Meta': {'object_name': 'TagObject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'cosinnus_file.fileentry': {
            'Meta': {'ordering': "[u'-uploaded_date', u'name']", 'object_name': 'FileEntry'},
            '_sourcefilename': ('django.db.models.fields.CharField', [], {'default': "u'download'", 'max_length': '100'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '250'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cosinnus_file_fileentry_set'", 'on_delete': 'models.PROTECT', 'to': u"orm['cosinnus.CosinnusGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isfolder': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'media_tag': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cosinnus.TagObject']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'default': "u'/'", 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '55'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uploaded_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'files'", 'on_delete': 'models.PROTECT', 'to': u"orm['auth.User']"}),
            'uploaded_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        }
    }

    complete_apps = ['cosinnus_file']