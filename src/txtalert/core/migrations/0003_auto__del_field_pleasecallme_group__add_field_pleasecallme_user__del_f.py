# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(username='kumbu')
        
        # Deleting field 'PleaseCallMe.group'
        db.delete_column('core_pleasecallme', 'group_id')

        # Adding field 'PleaseCallMe.user'
        db.add_column('core_pleasecallme', 'user', self.gf('django.db.models.fields.related.ForeignKey')(default=user.pk, to=orm['auth.User']), keep_default=False)

        # Deleting field 'Patient.group'
        db.delete_column('core_patient', 'group_id')

        # Adding field 'Patient.user'
        db.add_column('core_patient', 'user', self.gf('django.db.models.fields.related.ForeignKey')(default=user.pk, to=orm['auth.User']), keep_default=False)

        # Deleting field 'HistoricalPatient.group'
        db.delete_column('core_historicalpatient', 'group_id')

        # Adding field 'HistoricalPatient.user'
        db.add_column('core_historicalpatient', 'user', self.gf('django.db.models.fields.related.ForeignKey')(default=user.pk, to=orm['auth.User']), keep_default=False)

        # Deleting field 'Clinic.group'
        db.delete_column('core_clinic', 'group_id')

        # Adding field 'Clinic.user'
        db.add_column('core_clinic', 'user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='clinic', null=True, to=orm['auth.User']), keep_default=False)


    def backwards(self, orm):
        
        # all previous data belongs to Temba Lethu Clinic
        from django.contrib.auth.models import Group
        group, created = Group.objects.get_or_create(name="Temba Lethu")
        
        # Adding field 'PleaseCallMe.group'
        db.add_column('core_pleasecallme', 'group', self.gf('django.db.models.fields.related.ForeignKey')(default=group.pk, to=orm['auth.Group']), keep_default=False)

        # Deleting field 'PleaseCallMe.user'
        db.delete_column('core_pleasecallme', 'user_id')

        # Adding field 'Patient.group'
        db.add_column('core_patient', 'group', self.gf('django.db.models.fields.related.ForeignKey')(default=group.pk, to=orm['auth.Group']), keep_default=False)

        # Deleting field 'Patient.user'
        db.delete_column('core_patient', 'user_id')

        # Adding field 'HistoricalPatient.group'
        db.add_column('core_historicalpatient', 'group', self.gf('django.db.models.fields.related.ForeignKey')(default=group.pk, to=orm['auth.Group']), keep_default=False)

        # Deleting field 'HistoricalPatient.user'
        db.delete_column('core_historicalpatient', 'user_id')

        # Adding field 'Clinic.group'
        db.add_column('core_clinic', 'group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='clinic', null=True, to=orm['auth.Group'], blank=True), keep_default=False)

        # Deleting field 'Clinic.user'
        db.delete_column('core_clinic', 'user_id')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.clinic': {
            'Meta': {'object_name': 'Clinic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'te_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'clinic'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'core.historicalpatient': {
            'Meta': {'ordering': "('-history_id',)", 'object_name': 'HistoricalPatient'},
            'active_msisdn': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.MSISDN']", 'null': 'True', 'blank': 'True'}),
            'age': ('django.db.models.fields.IntegerField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deceased': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'disclosed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'history_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['core.Language']"}),
            'last_clinic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Clinic']", 'null': 'True', 'blank': 'True'}),
            'opted_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'risk_profile': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'te_id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.historicalvisit': {
            'Meta': {'ordering': "('-history_id',)", 'object_name': 'HistoricalVisit'},
            'clinic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Clinic']"}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'history_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Patient']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'te_visit_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'visit_type': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
        },
        'core.language': {
            'Meta': {'object_name': 'Language'},
            'attended_message': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'missed_message': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tomorrow_message': ('django.db.models.fields.TextField', [], {}),
            'twoweeks_message': ('django.db.models.fields.TextField', [], {})
        },
        'core.msisdn': {
            'Meta': {'ordering': "['-id']", 'object_name': 'MSISDN'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msisdn': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'core.patient': {
            'Meta': {'ordering': "['created_at']", 'object_name': 'Patient'},
            'active_msisdn': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.MSISDN']", 'null': 'True', 'blank': 'True'}),
            'age': ('django.db.models.fields.IntegerField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deceased': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'disclosed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['core.Language']"}),
            'last_clinic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Clinic']", 'null': 'True', 'blank': 'True'}),
            'msisdns': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'contacts'", 'symmetrical': 'False', 'to': "orm['core.MSISDN']"}),
            'opted_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'risk_profile': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'te_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.pleasecallme': {
            'Meta': {'object_name': 'PleaseCallMe'},
            'clinic': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pcms'", 'null': 'True', 'to': "orm['core.Clinic']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msisdn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pcms'", 'to': "orm['core.MSISDN']"}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'default': "'nc'", 'max_length': '2'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.visit': {
            'Meta': {'ordering': "['date']", 'object_name': 'Visit'},
            'clinic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Clinic']"}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Patient']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'te_visit_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'visit_type': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
        }
    }

    complete_apps = ['core']
