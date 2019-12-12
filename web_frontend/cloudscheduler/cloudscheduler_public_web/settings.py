"""
Django settings for cloudscheduler project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from cloudscheduler.lib.db_config import *
config = Config('/etc/cloudscheduler/cloudscheduler.yaml', ['web_frontend','signal_manager', 'glintPoller.py'], db_config_dict=True, pool_size=10, max_overflow=10, refreshable=True)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sa$jy+6m=w$nn=1i*=7_i)=p21ubbw65=(*(ubuo!fhy-zf$$='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Profiling
if config.categories["web_frontend"]["enable_profiling"]:
    SILKY_PYTHON_PROFILER = True
    SILKY_PYTHON_PROFILER_BINARY = True
    SILKY_PYTHON_PROFILER_RESULT_PATH = "/var/www/silkydata/"
    SILKY_MAX_RECORDED_REQUESTS = 250 #for a large scale test this should probably be higher but this should be plenty for us
    SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10
    # command to manually clear request log: python3 manage.py silk_clear_request_log

ALLOWED_HOSTS = [
                'csv2-dev-public.heprc.uvic.ca',
                'csv2-dev-public-wsgi.heprc.uvic.ca'
                ]

APPEND_SLASH = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'applogfile': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': config.categories["web_frontend"]["log_file"],
            'maxBytes': 1024*1024*15, # 15MB
            'backupCount': 10,
            'formatter': 'simple'
        },
    },
    'loggers': {
        'glintv2': {
            'handlers': ['applogfile'],
            'level': 'INFO',
        },
    }
}


# Application definition
if config.categories["web_frontend"]["enable_profiling"]:
    INSTALLED_APPS = [
        'silk',
        'csv2.apps.Csv2Config',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'mathfilters',
    ]
else:
    INSTALLED_APPS = [
        'csv2.apps.Csv2Config',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'mathfilters',
    ]
if config.categories["web_frontend"]["enable_glint"]:
    INSTALLED_APPS.append('glintwebui.apps.GlintwebuiConfig')


if config.categories["web_frontend"]["enable_profiling"]:
    MIDDLEWARE = [
        'silk.middleware.SilkyMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.RemoteUserMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
else:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.RemoteUserMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.RemoteUserBackend',
]


ROOT_URLCONF = 'cloudscheduler_public_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cloudscheduler_public_web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': config.db_config['db_host'],
        'PORT': config.db_config['db_port'],
        'NAME': config.db_config['db_name'],
        'USER': config.db_config['db_user'],
        'PASSWORD': config.db_config['db_password'],
    }
}
del config.db_config
CSV2_CONFIG = config

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Vancouver'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

#STATICFILES_DIRS = (
#    os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/static/',
#)

STATIC_URL = '/static/'
STATIC_ROOT = '/opt/cloudscheduler/web_frontend/cloudscheduler/csv2/static/'

# Celery variables
# not sure if it should be json for sure or not yet.
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Canada/Pacific'
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_DEFAULT_QUEUE = 'tx_requests'
CELERY_DEFAULT_EXCHANGE = "tx_requests"

CELERY_QUEUES = {
    "pull_requests": {"exchange": "pull_requests"},
    "tx_requests": {"exchange": "tx_requests"},
}
CELERY_ROUTES = {
    'Glintv2.glintv2.tasks.pull_request': {'queue': 'pull_requests'},
    'Glintv2.glintv2.tasks.tx_request': {'queue': 'tx_requests'},
}
