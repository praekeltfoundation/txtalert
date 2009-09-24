# Copyright (c) 2009, Jurie-Jan Botha
#
# This file is part of the 'cron' Django application.
#
# 'sms' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# 'sms' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the 'sms' application. If not, see
# <http://www.gnu.org/licenses/>.


from urllib import urlopen, urlencode
from datetime import datetime
from xml.etree import cElementTree as et
from django.db import models


class Gateway(models.Model):
    name = models.CharField('Name', max_length=64, unique=True)
    url = models.URLField('URL', verify_exists=False)

    class Meta:
        verbose_name = 'Gateway'
        verbose_name_plural = 'Gateways'

    def __unicode__(self):
        return self.name

    def logAction(self, start, end, results, message):
        message, created = SMSMessage.objects.get_or_create(message=message)
        action = SMSSendAction.objects.create(gateway=self, message=message, start=start, end=end)
        for msisdn, result in results:
            contact, created = Contact.objects.get_or_create(msisdn=msisdn)
            SMSLog.objects.create(action=action, contact=contact, result=result)
        return action


class OperaGateway(Gateway):
    method = models.CharField('Method', max_length=64)
    service = models.IntegerField('Service')
    password = models.CharField('Password', max_length=64)
    channel = models.IntegerField('Channel')

    class Meta:
        verbose_name = 'Opera Gateway'
        verbose_name_plural = 'Opera Gateways'

    def __unicode__(self):
        return self.name

    def sendSMS(self, msisdns, message):
        if len(msisdns) == 0: raise RuntimeError('The msisdn parameter cannot contain an empty list.')
        # alter numbers set to suit gateway
        # remove duplicate numbers
        numbers = list(set(msisdns))
        # prepend a standard networ name
        numbers = [('vodacom-za.+' + n) for n in numbers]
        # turn into one string
        numbers = ','.join(numbers)

        # build post data
        post = {
            'Method': self.method,
            'Service': self.service,
            'Password': self.password,
            'Channel': self.channel,
            'Numbers': numbers,
            'SMSText': message,
        }

        # send web communication and parse the response
        try:
            response = urlopen(self.url, urlencode(post)).read()
            et.fromstring(response)
        except: raise Exception(response)

        # log the action
        results = [(m, 'u') for m in msisdns]
        return self.logAction(datetime.now(), datetime.now(), results, message)


class MessageTemplate(models.Model):
    name = models.CharField('Name', max_length=64, unique=True)
    template = models.TextField('Template')
    
    class Meta:
        verbose_name = 'Message Template'
        verbose_name_plural = 'Message Templates'

    def __unicode__(self):
        return self.name


class Service(models.Model):
    name = models.CharField('Name', max_length=64, unique=True)
    gateway = models.ForeignKey(Gateway, related_name='services')
    template = models.ForeignKey(MessageTemplate, related_name='services')

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __unicode__(self):
        return self.name


class ContactFilter(models.Model):
    name = models.CharField('Name', max_length=64, unique=True)
    filter = models.TextField('Filter')
    service = models.ForeignKey(Service, related_name='contactsets')

    class Meta:
        verbose_name = 'Contact Set'
        verbose_name_plural = 'Contact Sets'
    
    def __unicode__(self):
        return self.name


class Contact(models.Model):
    msisdn = models.CharField('MSISDN', max_length=32)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def __unicode__(self):
        return self.msisdn


class SMSMessage(models.Model):
    message = models.TextField()

    class Meta:
        verbose_name = 'SMS Message'
        verbose_name_plural = 'SMS Messages'

    def __unicode__(self):
        return self.message


class SMSSendAction(models.Model):
    gateway = models.ForeignKey(Gateway, related_name='smssendactions')
    message = models.ForeignKey(SMSMessage, related_name='smssendactions')
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        verbose_name = 'SMS Send Action'
        verbose_name_plural = 'SMS Send Actions'

    def __unicode__(self):
        return "%s" % (self.gateway,)


class SMSLog(models.Model):
    RESULT_CHOICES = (
        ('u', 'undetermined'),
        ('s', 'successfull'),
        ('f', 'failed'),
    )

    action = models.ForeignKey(SMSSendAction, related_name='smslogs')
    contact = models.ForeignKey(Contact, related_name='smslogs')
    result = models.CharField('Result', max_length=1, default='u')

    class Meta:
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'
    
    def __unicode__(self):
        return self.result
