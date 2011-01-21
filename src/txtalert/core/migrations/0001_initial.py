# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MSISDN'
        db.create_table('core_msisdn', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('msisdn', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
        ))
        db.send_create_signal('core', ['MSISDN'])

        # Adding model 'Language'
        db.create_table('core_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('missed_message', self.gf('django.db.models.fields.TextField')()),
            ('attended_message', self.gf('django.db.models.fields.TextField')()),
            ('tomorrow_message', self.gf('django.db.models.fields.TextField')()),
            ('twoweeks_message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('core', ['Language'])

        # Adding model 'Clinic'
        db.create_table('core_clinic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('te_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='clinic', null=True, to=orm['auth.Group'])),
        ))
        db.send_create_signal('core', ['Clinic'])

        # Adding model 'HistoricalPatient'
        db.create_table('core_historicalpatient', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('te_id', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('active_msisdn', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.MSISDN'], null=True, blank=True)),
            ('age', self.gf('django.db.models.fields.IntegerField')()),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('opted_in', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('disclosed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deceased', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_clinic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Clinic'], null=True, blank=True)),
            ('risk_profile', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['core.Language'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('core', ['HistoricalPatient'])

        # Adding model 'Patient'
        db.create_table('core_patient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('te_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('active_msisdn', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.MSISDN'], null=True, blank=True)),
            ('age', self.gf('django.db.models.fields.IntegerField')()),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('opted_in', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('disclosed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deceased', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_clinic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Clinic'], null=True, blank=True)),
            ('risk_profile', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['core.Language'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('core', ['Patient'])

        # Adding M2M table for field msisdns on 'Patient'
        db.create_table('core_patient_msisdns', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patient', models.ForeignKey(orm['core.patient'], null=False)),
            ('msisdn', models.ForeignKey(orm['core.msisdn'], null=False))
        ))
        db.create_unique('core_patient_msisdns', ['patient_id', 'msisdn_id'])

        # Adding model 'HistoricalVisit'
        db.create_table('core_historicalvisit', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Patient'])),
            ('te_visit_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('comment', self.gf('django.db.models.fields.TextField')(default='')),
            ('clinic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Clinic'])),
            ('visit_type', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('core', ['HistoricalVisit'])

        # Adding model 'Visit'
        db.create_table('core_visit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Patient'])),
            ('te_visit_id', self.gf('django.db.models.fields.CharField')(max_length=20, unique=True, null=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('comment', self.gf('django.db.models.fields.TextField')(default='')),
            ('clinic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Clinic'])),
            ('visit_type', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('core', ['Visit'])

        # Adding model 'PleaseCallMe'
        db.create_table('core_pleasecallme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('msisdn', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pcms', to=orm['core.MSISDN'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('reason', self.gf('django.db.models.fields.CharField')(default='nc', max_length=2)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('clinic', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pcms', null=True, to=orm['core.Clinic'])),
        ))
        db.send_create_signal('core', ['PleaseCallMe'])


    def backwards(self, orm):
        
        # Deleting model 'MSISDN'
        db.delete_table('core_msisdn')

        # Deleting model 'Language'
        db.delete_table('core_language')

        # Deleting model 'Clinic'
        db.delete_table('core_clinic')

        # Deleting model 'HistoricalPatient'
        db.delete_table('core_historicalpatient')

        # Deleting model 'Patient'
        db.delete_table('core_patient')

        # Removing M2M table for field msisdns on 'Patient'
        db.delete_table('core_patient_msisdns')

        # Deleting model 'HistoricalVisit'
        db.delete_table('core_historicalvisit')

        # Deleting model 'Visit'
        db.delete_table('core_visit')

        # Deleting model 'PleaseCallMe'
        db.delete_table('core_pleasecallme')


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
        'core.clinic': {
            'Meta': {'object_name': 'Clinic'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'clinic'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'te_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'})
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
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.pleasecallme': {
            'Meta': {'object_name': 'PleaseCallMe'},
            'clinic': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pcms'", 'null': 'True', 'to': "orm['core.Clinic']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msisdn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pcms'", 'to': "orm['core.MSISDN']"}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'default': "'nc'", 'max_length': '2'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
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
