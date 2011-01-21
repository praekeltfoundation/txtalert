# Copyright (c) 2009, Jurie-Jan Botha
#
# This file is part of the 'settings' Django application.
#
# 'settings' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# 'settings' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the 'settings' application. If not, see
# <http://www.gnu.org/licenses/>.


from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Setting(models.Model):
    TYPE_CHOICES = (
        ('n', 'Number'),
        ('t', 'Text'),
        ('o', 'Object'),
    )

    name = models.CharField('Name', max_length=255, unique=True)
    type = models.CharField('Type', max_length=1, choices=TYPE_CHOICES, default='n', blank=False)
    removable = models.BooleanField('Removable', default=True)
    int_value = models.IntegerField('Integer Value', blank=True, null=True)
    text_value = models.TextField('Text Value', blank=True, null=True)
    object_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object_value = generic.GenericForeignKey('object_type', 'object_id')

    class Meta:
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'

    def getvalue(self):
        if self.type == 'n': return self.int_value
        elif self.type == 't': return self.text_value
        elif self.type == 'o': return self.object_value
        else: return None

    def setvalue(self, value):
        if self.type == 'n': self.int_value = value
        elif self.type == 't': self.text_value = value
        elif self.type == 'o': self.object_value = value
        else: return None

    value = property(getvalue, setvalue)

    def __unicode__(self):
        return self.name
