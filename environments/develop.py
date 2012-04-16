from txtalert.env.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'txtalert_dev',
        'USER': 'txtalert',
        'PASSWORD': 'txtalert',
        'HOST': 'localhost',
        'PORT': ''
    }
}
