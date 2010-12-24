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

from environments.defaults import *
import os

DEBUG = False

DATABASE_ENGINE = 'mysql'
DATABASE_HOST = '41.203.21.92'
DATABASE_NAME = 'txtalert_production'
DATABASE_USER = 'txtalertuser'
DATABASE_PASSWORD = 'phohX7mo'
DATABASE_PORT = ''

OPERA_SERVICE = '19079'
OPERA_PASSWORD = 'zu8U6afR'
OPERA_CHANNEL = '165'

ADMINS = MANAGERS = (
    ('Simon de Haan', 'simon@praekeltfoundation.org'),
    ('David Maclay', 'david@praekeltfoundation.org'),
)

PISTON_EMAIL_ERRORS = True
PISTON_DISPLAY_ERRORS = True
