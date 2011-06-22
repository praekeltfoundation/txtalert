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

APP_ROOT = os.getcwd()
PROJECT_NAME = os.path.basename(APP_ROOT)

SECRET_KEY = ''

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'txtalert_dev',
        'USER': '',
        'PASSWORD': '',
        'PORT': ''
    }
}

ADMINS = (
    ('Foundation Developers', 'dev+txtalert@praekeltfoundation.org'),
)

MANAGERS = ADMINS

SERVER_EMAIL = 'txtalert@txtalert.praekeltfoundation.org'

EMAIL_SUBJECT_PREFIX = '[txtAlert] '

TIME_ZONE = 'Africa/Johannesburg'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True

UPLOAD_ROOT = "upload"
MEDIA_URL = '/media/'
MEDIA_ROOT = join(APP_ROOT, 'webroot', 'media')
STATIC_URL = '/static/'
STATIC_ROOT = join(APP_ROOT, 'webroot', 'static')

AUTH_PROFILE_MODULE = 'core.AuthProfile'
LOGIN_URL = '/bookings/sign-in/'
LOGOUT_URL = '/bookings/sign-out/'
LOGIN_REDIRECT_URL = '/bookings/'

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
#    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'txtalert.apps.bookings.bookings_admin.context_processors.change_requests',
)


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'txtalert.core.auth.backends.PatientBackend'
)

TEMPLATE_DIRS = (
    'templates',
)

ROOT_URLCONF = 'txtalert.urls'

INSTALLED_APPS = (
    'txtalert.core',
    'txtalert.apps.general.settings',
    'txtalert.apps.general.jquery',
    'txtalert.apps.therapyedge',
    'txtalert.apps.bookings',
    'txtalert.apps.widget',
    'txtalert.apps.gateway',
    'txtalert.apps.api',
    'txtalert.apps.cd4',
    'piston',
    'dirtyfields',
    'history',
    'south',
    'gunicorn',
    'django_nose',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.markup',
)

SMS_GATEWAY_CLASS = 'txtalert.apps.gateway.backends.vumi'
VUMI_USERNAME = ''
VUMI_PASSWORD = ''

BOOKING_TOOL_RISK_LEVELS = {
    # pc is for patient count
    'high': lambda pc: pc > 100,
    'medium': lambda pc: 50 <= pc <= 100,
    'low': lambda pc: pc < 50,
}

SOUTH_TESTS_MIGRATE = False 
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
