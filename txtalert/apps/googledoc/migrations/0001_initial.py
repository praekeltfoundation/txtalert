# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GoogleAccount'
        db.create_table('googledoc_googleaccount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('googledoc', ['GoogleAccount'])

        # Adding model 'SpreadSheet'
        db.create_table('googledoc_spreadsheet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('spreadsheet', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['googledoc.GoogleAccount'])),
        ))
        db.send_create_signal('googledoc', ['SpreadSheet'])


    def backwards(self, orm):
        
        # Deleting model 'GoogleAccount'
        db.delete_table('googledoc_googleaccount')

        # Deleting model 'SpreadSheet'
        db.delete_table('googledoc_spreadsheet')


    models = {
        'googledoc.googleaccount': {
            'Meta': {'ordering': "['-id']", 'object_name': 'GoogleAccount'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'googledoc.spreadsheet': {
            'Meta': {'ordering': "['-id']", 'object_name': 'SpreadSheet'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['googledoc.GoogleAccount']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'spreadsheet': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['googledoc']
