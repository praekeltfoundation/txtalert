# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CD4Record'
        db.create_table('cd4_cd4record', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cd4document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cd4.CD4Document'])),
            ('lab_id_number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('msisdn', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('cd4count', self.gf('django.db.models.fields.IntegerField')()),
            ('sms', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gateway.SendSMS'], null=True, blank=True)),
        ))
        db.send_create_signal('cd4', ['CD4Record'])

        # Adding model 'CD4Document'
        db.create_table('cd4_cd4document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('original', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('cd4', ['CD4Document'])


    def backwards(self, orm):
        
        # Deleting model 'CD4Record'
        db.delete_table('cd4_cd4record')

        # Deleting model 'CD4Document'
        db.delete_table('cd4_cd4document')


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
        'cd4.cd4document': {
            'Meta': {'object_name': 'CD4Document'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'cd4.cd4record': {
            'Meta': {'object_name': 'CD4Record'},
            'cd4count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lab_id_number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'msisdn': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'sms': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gateway.SendSMS']", 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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

    complete_apps = ['cd4']
