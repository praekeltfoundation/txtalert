from django.test import TestCase
from txtalert.apps.cd4.utils import read_cd4_document

class CD4TestCase(TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_parsing_of_sample_excel(self):
        """
        We should be able to read the sample MS Excel document
        """
        rows = read_cd4_document('docs/sample.xls')
        # there should be 4 rows
        self.assertEquals(len(rows), 4)
        for row in rows:
            # each with 5 columns
            self.assertEquals(len(row), 5)
    
    