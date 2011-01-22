# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # all previous data belongs to Temba Lethu Clinic
        from django.contrib.auth.models import Group
        group, created = Group.objects.get_or_create(name="Temba Lethu")
        
        # Adding field 'SendSMS.group'
        db.add_column('gateway_sendsms', 'group', self.gf('django.db.models.fields.related.ForeignKey')(default=group.pk, to=orm['auth.Group']), keep_default=False)

        # Adding field 'PleaseCallMe.group'
        db.add_column('gateway_pleasecallme', 'group', self.gf('django.db.models.fields.related.ForeignKey')(default=group.pk, related_name='gateway_pleasecallme_set', to=orm['auth.Group']), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'SendSMS.group'
        db.delete_column('gateway_sendsms', 'group_id')

        # Deleting field 'PleaseCallMe.group'
        db.delete_column('gateway_pleasecallme', 'group_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gateway.pleasecallme': {
            'Meta': {'ordering': "['created_at']", 'object_name': 'PleaseCallMe'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gateway_pleasecallme_set'", 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'recipient_msisdn': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sender_msisdn': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sms_id': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'gateway.sendsms': {
            'Meta': {'object_name': 'SendSMS'},
            'delivery': ('django.db.models.fields.DateTimeField', [], {}),
            'delivery_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'expiry': ('django.db.models.fields.DateTimeField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'msisdn': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'priority': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'receipt': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'smstext': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'v'", 'max_length': '1'})
        }
    }

    complete_apps = ['gateway']
