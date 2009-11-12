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


from os.path import join
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler

APP_ROOT = os.path.abspath(join(os.path.dirname(__file__),'..'))
PROJECT_NAME = os.path.basename(APP_ROOT)

# Initialize logger that's rotated daily
LOG_FORMAT = '[%(name)s] %(asctime)s %(levelname)s %(message)s'
LOG_FILE = join(APP_ROOT, 'log/%s.log' % PROJECT_NAME)

LOGGER = logging.getLogger()
LOGGER.name = PROJECT_NAME
LOGGER.level = logging.DEBUG

# Due to a stupid bug in Django it'll load the settings file twice unless 
# ./manage.py is called with the --settings option set. This potentially
# creates two different loggers doing exactly the same thing. So we check if 
# the current list of handlers already contains an instance of TimedRotatingFileHandler
if not any(isinstance(h, TimedRotatingFileHandler) for h in LOGGER.handlers):
    handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', backupCount=14)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    LOGGER.addHandler(handler)

# Add APP_ROOT/apps to the load path
APP_PATH = join(APP_ROOT, 'apps')
sys.path.insert(0, APP_PATH)

# Add APP_ROOT/lib to the load path
LIB_PATH = join(APP_ROOT, 'lib')
sys.path.insert(0, LIB_PATH)

SECRET_KEY = ''

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TEST_DATABASE_CHARSET = 'utf8'

ADMINS = (
    ('Joe Developer', 'a@b.xyz'),
)

MANAGERS = ADMINS

SERVER_EMAIL = 'a@b.xyz'

EMAIL_SUBJECT_PREFIX = '[TxtAlert] '
EMAIL_HOST = 'smtp.somehost.xyz'
EMAIL_PORT = 25
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'email_user'
EMAIL_HOST_PASSWORD = 'email_user_password'

TIME_ZONE = 'Africa/Johannesburg'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True

MEDIA_ROOT = join(APP_ROOT, 'webroot', 'media')
MEDIA_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/media/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_DIRS = (
    join(APP_ROOT, 'templates')
)

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'general.settings',
    'general.cron',
    'general.jquery',
    'mobile.sms',
    'therapyedge',
    'bookingtool',
    'opera',
    'dirtyfields',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
)

BOOKING_TOOL_RISK_LEVELS = {
    # pc is for patient count
    'high': lambda pc: pc > 100,
    'medium': lambda pc: 50 <= pc < 100,
    'low': lambda pc: pc < 50,
}
