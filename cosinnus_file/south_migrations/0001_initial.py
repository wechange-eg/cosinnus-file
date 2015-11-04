# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FileEntry'
        db.create_table(u'cosinnus_file_fileentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('media_tag', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cosinnus.TagObject'], unique=True, null=True, on_delete=models.PROTECT, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'cosinnus_file_fileentry_set', on_delete=models.PROTECT, to=orm['auth.Group'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=55)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=250)),
            ('uploaded_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('uploaded_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'files', on_delete=models.PROTECT, to=orm['auth.User'])),
        ))
        db.send_create_signal(u'cosinnus_file', ['FileEntry'])

        # Adding unique constraint on 'FileEntry', fields ['group', 'slug']
        db.create_unique(u'cosinnus_file_fileentry', ['group_id', 'slug'])


    def backwards(self, orm):
        # Removing unique constraint on 'FileEntry', fields ['group', 'slug']
        db.delete_unique(u'cosinnus_file_fileentry', ['group_id', 'slug'])

        # Deleting model 'FileEntry'
        db.delete_table(u'cosinnus_file_fileentry')


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
        u'cosinnus.tagobject': {
            'Meta': {'object_name': 'TagObject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'cosinnus_file.fileentry': {
            'Meta': {'ordering': "[u'-uploaded_date', u'name']", 'unique_together': "((u'group', u'slug'),)", 'object_name': 'FileEntry'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '250'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cosinnus_file_fileentry_set'", 'on_delete': 'models.PROTECT', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_tag': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cosinnus.TagObject']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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