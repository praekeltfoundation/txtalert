#  This file is part of TxtAlert.
#
#  TxtALert is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TxtAlert is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with TxtAlert.  If not, see <http://www.gnu.org/licenses/>.


import re


class ImportEvent(object):
    _types = ('error', 'new', 'update')

    def __init__(self):
        self.type = None
        self.messages = []

    def __str__(self):
        return '\n'.join(self.messages)

    def _validateType(self, type):
        if type.__class__ is not str:
            raise TypeError('Type argument has to be be of type string.')
        if type not in self._types:
            raise ValueError('Type argument value has to be one of the following %s.' % (self._types))
        return type

    def _validateMessage(self, message):
        if type(message) is not str:
            raise TypeError('Message argument has to be of type string or None.')
        return message

    def append(self, message, type):
        type = self._validateType(type)
        if self.type == 'new':
            if type != 'update':
                self.type = type
        else: self.type = type
        self.messages.append(self._validateMessage(message))

    def isError(self):
        return self.type == 'error'


class ImportEvents(object):
    _events = []

    def __init__(self):
        self.error_messages = []
        self.errors = 0
        self.new = 0
        self.updated = 0

    def append(self, event):
        self._events.append(event)
        
        if event.type == 'error':
            self.error_messages += event.messages
            self.errors += 1
        elif event.type == 'new':
            self.new += 1
        elif event.type == 'update':
            self.updated += 1

    def extend(self, events):
        self.errors += events.errors
        self.updated += events.updated
        self.new += events.new
        self.error_messages.extend(events.error_messages)
