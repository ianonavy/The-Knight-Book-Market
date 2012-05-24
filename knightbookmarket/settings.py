# Django settings for knightbookmarket project.

import os
import django

DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
settings_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
IS_DOTCLOUD = SITE_ROOT.find('dotcloud') != -1

password_file = open(os.path.join(SITE_ROOT, 'passwords.txt'))
def next_password():
    return password_file.readline().strip()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Ian Adam Naval', 'ianonavy@gmail.com'),
)

MANAGERS = ADMINS

if IS_DOTCLOUD:
    DATABASES = {
	'default': {
	   'ENGINE': 'django.db.backends.postgresql_psycopg2',
	    'NAME': 'dotcloud',
	    'USER': 'root',
	    'PASSWORD': next_password(),
	    'HOST': 'knightbookmarket-ianonavy.dotcloud.com',
	    'PORT': '11810',
	}
    }
else:
    next_password()
    DATABASES = {
	'default': {
	    'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(SITE_ROOT, 'development.db')
	}
    }


TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = '/home/dotcloud/data/media'
MEDIA_URL = '/media/'
STATIC_ROOT = '/home/dotcloud/volatile/static'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = next_password()

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'knightbookmarket.urls'

WSGI_APPLICATION = 'knightbookmarket.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'core/templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'core',
    'django_facebook',
    'django_evolution',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django_facebook.context_processors.facebook',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

AUTHENTICATION_BACKENDS = (
    'django_facebook.auth_backends.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_PROFILE_MODULE = 'django_facebook.FacebookProfile'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

FACEBOOK_APP_ID = next_password()
FACEBOOK_APP_SECRET = next_password()

LOGIN_REDIRECT_URL = '/'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'knightbookmarket@gmail.com'
EMAIL_HOST_PASSWORD = next_password()
EMAIL_PORT = 587