"""
Django settings for jelf project.  
For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(__file__)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!$e(y9&5ol=#s7wex!xhv=f&5f2@ufjez3ee9kdifw=41p_+%*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

USE_TZ = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, '..', 'templates/'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

#FIXTURE_DIRS = (
#   os.path.join(BASE_DIR, '..', 'fixtures/'),
#)

ALLOWED_HOSTS = ['*']

TEMPLATE_LOADERS = (
    'django_jinja.loaders.AppLoader',
    'django_jinja.loaders.FileSystemLoader',
)
DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.html'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_jinja',
    'timelog',
    'coursemanager',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'jelf.db'),
    }
}

MEDIA_ROOT = os.path.join(BASE_DIR, '..', "media")
MEDIA_URL = "/media/"

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '..', "static"),
)

LOG_PATH = os.path.join(BASE_DIR, '..', 'logs/')
TIMELOG_LOG = os.path.join(LOG_PATH, 'timelog.log')
SQL_LOG = os.path.join(LOG_PATH, 'sqllog.log')

LOGGING = {
  'version': 1,
  'formatters': {
    'plain': {
      'format': '%(asctime)s %(message)s'},
    },
  'handlers': {
    'timelog': {
      'level': 'DEBUG',
      'class': 'logging.handlers.RotatingFileHandler',
      'filename': TIMELOG_LOG,
      'maxBytes': 1024 * 1024 * 5,  # 5 MB
      'backupCount': 5,
      'formatter': 'plain',
    },
    'sqllog': {
      'level': 'DEBUG',
      'class': 'logging.handlers.RotatingFileHandler',
      'filename': SQL_LOG,
      'maxBytes': 1024 * 1024 * 5,  # 5 MB
      'backupCount': 5,
      'formatter': 'plain',
    },
  },
  'loggers': {
    'timelog.middleware': {
      'handlers': ['timelog'],
      'level': 'DEBUG',
      'propogate': False,
     },
    'timing_logging': {
      'handlers': ['timelog'],
      'level': 'DEBUG',
      'propogate': False,
     },
    'logging_middleware': {
      'handlers': ['sqllog'],
      'level': 'DEBUG',
      'propogate': False
    },
  },
}
