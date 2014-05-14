# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'FileEntry.isfolder'
        db.delete_column(u'cosinnus_file_fileentry', 'isfolder')

        # Adding field 'FileEntry.is_container'
        db.add_column(u'cosinnus_file_fileentry', 'is_container',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'FileEntry.media_tag'
        db.alter_column(u'cosinnus_file_fileentry', 'media_tag_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['neww.NewwTagObject'], unique=True, null=True, on_delete=models.PROTECT))

    def backwards(self, orm):
        # Adding field 'FileEntry.isfolder'
        db.add_column(u'cosinnus_file_fileentry', 'isfolder',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'FileEntry.is_container'
        db.delete_column(u'cosinnus_file_fileentry', 'is_container')


        # Changing field 'FileEntry.media_tag'
        db.alter_column(u'cosinnus_file_fileentry', 'media_tag_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cosinnus.TagObject'], unique=True, null=True, on_delete=models.PROTECT))

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
        u'cosinnus.attachedobject': {
            'Meta': {'ordering': "(u'content_type',)", 'unique_together': "((u'content_type', u'object_id'),)", 'object_name': 'AttachedObject'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'cosinnus.cosinnusgroup': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'CosinnusGroup'},
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_tag': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['neww.NewwTagObject']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'cosinnus_groups'", 'blank': 'True', 'through': u"orm['cosinnus.CosinnusGroupMembership']", 'to': u"orm['auth.User']"})
        },
        u'cosinnus.cosinnusgroupmembership': {
            'Meta': {'unique_together': "((u'user', u'group'),)", 'object_name': 'CosinnusGroupMembership'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'memberships'", 'to': u"orm['cosinnus.CosinnusGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cosinnus_memberships'", 'to': u"orm['auth.User']"})
        },
        u'cosinnus_file.fileentry': {
            'Meta': {'ordering': "[u'-created', u'title']", 'unique_together': "((u'group', u'slug'),)", 'object_name': 'FileEntry'},
            '_sourcefilename': ('django.db.models.fields.CharField', [], {'default': "u'download'", 'max_length': '100'}),
            'attached_objects': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['cosinnus.AttachedObject']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cosinnus_file_fileentry_set'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['auth.User']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cosinnus_file_fileentry_set'", 'on_delete': 'models.PROTECT', 'to': u"orm['cosinnus.CosinnusGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_container': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'media_tag': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['neww.NewwTagObject']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'default': "u'/'", 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '55', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'neww.newwtagobject': {
            'Meta': {'object_name': 'NewwTagObject'},
            'approach': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'null': 'True', 'to': u"orm['cosinnus.CosinnusGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'likers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'likes+'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'likes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'location': ('osm_field.fields.OSMField', [], {'null': 'True', 'blank': 'True'}),
            u'location_lat': ('osm_field.fields.LatitudeField', [], {'null': 'True', 'blank': 'True'}),
            u'location_lon': ('osm_field.fields.LongitudeField', [], {'null': 'True', 'blank': 'True'}),
            'persons': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'place': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'topics': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'valid_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'valid_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'visibility': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'blank': 'True'})
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