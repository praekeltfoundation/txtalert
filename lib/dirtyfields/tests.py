from django.core.management.color import no_style
from django.db import models
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.db.models.loading import load_app
from django.db import connection, transaction

from testingapp.models import TestModel

class DirtyFieldsMixinTestCase(TestCase):
    
    def setUp(self):
        """ugly work around for apps that are only needed when testing"""
        sql, pending_references = connection.creation.sql_create_model(TestModel, no_style())
        self._execute_sql(sql)
    
    def tearDown(self):
        sql = connection.creation.sql_destroy_model(TestModel, {}, no_style())
        self._execute_sql(sql)
    
    def _execute_sql(self, statements):
        for sql in statements:
            cursor = connection.cursor()
            cursor.execute(sql)
        transaction.set_dirty()
    
    def test_dirty_fields(self):
        tm = TestModel()
        # initial state shouldn't be dirty
        self.assertEqual(tm.get_dirty_fields(), {})
        
        # changing values should flag them as dirty
        tm.boolean = False
        tm.characters = 'testing'
        self.assertEqual(tm.get_dirty_fields(), {
            'boolean': True,
            'characters': ''
        })
        
        # resetting them to original values should unflag
        tm.boolean = True
        self.assertEqual(tm.get_dirty_fields(), {
            'characters': ''
        })
    
    def test_sweeping(self):
        from testingapp.models import TestModel
        tm = TestModel()
        tm.boolean = False
        tm.characters = 'testing'
        self.assertEqual(tm.get_dirty_fields(), {
            'boolean': True,
            'characters': ''
        })
        tm.save()
        self.assertEqual(tm.get_dirty_fields(), {})
    