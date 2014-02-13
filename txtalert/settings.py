# Django settings for txtalert project.

import os
from os.path import join

APP_ROOT = os.getcwd()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'txtalert.db',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Africa/Johannesburg'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# FIXME: txtAlert CD4 uses this
UPLOAD_ROOT = "upload"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = join(APP_ROOT, 'webroot', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = join(APP_ROOT, 'webroot', 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '^=%eyy8+8%&pvn-v@&+o^t336k-c4^=+-@g!zm-+zd*w%g^bwu'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'txtalert.core.auth.middleware.HttpBasicAuthMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'txtalert.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'txtalert.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    'templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'txtalert.core',
    'txtalert.apps.general.settings',
    'txtalert.apps.general.jquery',
    'txtalert.apps.therapyedge',
    'txtalert.apps.bookings',
    'txtalert.apps.widget',
    'txtalert.apps.gateway',
    'txtalert.apps.api',
    'txtalert.apps.cd4',
    'txtalert.apps.googledoc',
    'dirtyfields',
    'history',
    'south',
    'gunicorn',
    'django_nose',
    'raven.contrib.django.raven_compat',
    'markup_deprecated',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

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
    'django.contrib.messages.context_processors.messages',
    'txtalert.apps.bookings.bookings_admin.context_processors.change_requests',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'txtalert.core.auth.backends.PatientBackend',
    'txtalert.core.auth.backends.HttpBasicAuthBackend',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

SMS_GATEWAY_CLASS = 'txtalert.apps.gateway.backends.dummy'

BOOKING_TOOL_RISK_LEVELS = {
    # pc is for patient count
    'high': lambda pc: pc > 100,
    'medium': lambda pc: 50 <= pc <= 100,
    'low': lambda pc: pc < 50,
}

SOUTH_TESTS_MIGRATE = False
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

try:
    from production_settings import *
except ImportError:
    pass
