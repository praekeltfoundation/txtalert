from django.db import models


class GoogleAccount(models.Model):
    username = models.CharField('Google Username', max_length=250)
    password = models.CharField('Google Password', max_length=250)

    class Meta:
        verbose_name = 'Google Account'
        verbose_name_plural = 'Google Accounts'
        ordering=['-id']

    def __unicode__(self):
        return u'%s %s' % (self.username, self.password)


class SpreadSheet(models.Model):
    spreadsheet = models.CharField('SpreadSheet', max_length=200)
    account = models.ForeignKey(GoogleAccount)

    class Meta:
        verbose_name = 'Google SpreadSheet'
        verbose_name_plural = 'Google SpreadSheets'
        ordering=['-id']

    def __unicode__(self):
        return u'%s %s' % (self.spreadsheet, self.account)
