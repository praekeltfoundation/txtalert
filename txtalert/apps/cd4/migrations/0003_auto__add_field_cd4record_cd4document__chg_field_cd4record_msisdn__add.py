# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(username='kumbu')
        
        # Adding field 'CD4Document.user'
        db.add_column('cd4_cd4document', 'user', self.gf('django.db.models.fields.related.ForeignKey')(default=user.pk, to=orm['auth.User']), keep_default=False)
        
        # Deleting field 'CD4Document.user'
        db.delete_column('cd4_cd4document', 'group_id')

    def backwards(self, orm):
        
        # Deleting field 'CD4Document.user'
        db.delete_column('cd4_cd4document', 'user_id')
        
        from django.contrib.auth.models import Group
        group, created = Group.objects.get_or_create(name='Temba Lethu')
        
        # Adding field 'CD4Document.user'
        db.add_column('cd4_cd4document', 'group', self.gf('django.db.models.fields.related.ForeignKey')(default=group.pk, to=orm['auth.Group']), keep_default=False)
        
    
    
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
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cd4.cd4document': {
            'Meta': {'object_name': 'CD4Document'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cd4.cd4record': {
            'Meta': {'object_name': 'CD4Record'},
            'cd4count': ('django.db.models.fields.IntegerField', [], {}),
            'cd4document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'record_set'", 'to': "orm['cd4.CD4Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lab_id_number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'msisdn': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
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
