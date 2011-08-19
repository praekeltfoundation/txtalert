from django.db import models

class SpreadSheet(models.Model):
    spreadsheet = models.CharField('SpreadSheet Name', max_length=200)

    def __unicode__(self):
        return u'%s' % self.spreadsheet