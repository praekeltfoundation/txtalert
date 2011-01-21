# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SendSMS'
        db.create_table('gateway_sendsms', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('msisdn', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('smstext', self.gf('django.db.models.fields.TextField')()),
            ('delivery', self.gf('django.db.models.fields.DateTimeField')()),
            ('expiry', self.gf('django.db.models.fields.DateTimeField')()),
            ('priority', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('receipt', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('status', self.gf('django.db.models.fields.CharField')(default='v', max_length=1)),
            ('delivery_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('gateway', ['SendSMS'])

        # Adding model 'PleaseCallMe'
        db.create_table('gateway_pleasecallme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sms_id', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('sender_msisdn', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('recipient_msisdn', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('gateway', ['PleaseCallMe'])


    def backwards(self, orm):
        
        # Deleting model 'SendSMS'
        db.delete_table('gateway_sendsms')

        # Deleting model 'PleaseCallMe'
        db.delete_table('gateway_pleasecallme')


    models = {
        'gateway.pleasecallme': {
            'Meta': {'ordering': "['created_at']", 'object_name': 'PleaseCallMe'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
