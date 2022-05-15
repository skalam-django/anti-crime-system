from .base import *
from decouple import config

SERVER = 'PRODUCTION'

DEBUG = False
SECRET_KEY = config('ACS_SECRET_KEY') 
SERVICES = config('ACS_SERVICES')
AES128_CPIN = config('ACS_AES128_CPIN')  # 32 characters

ALLOWED_HOSTS = [
                  
                ]

INSTALLED_APPS += [
    'letsencrypt',
]


# SECURE_SSL_REDIRECT             =   True
# SECURE_PROXY_SSL_HEADER         =   ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_EXPIRE_AT_BROWSER_CLOSE =   False
# CSRF_COOKIE_SECURE              =   True
# SECURE_HSTS_SECONDS             =   100000
# SECURE_HSTS_INCLUDE_SUBDOMAINS  =   True
# SECURE_HSTS_PRELOAD             =   True
# SECURE_REDIRECT_EXEMPT          =   ["^insecure/"]

DATABASES = {
    'default': {
        'ENGINE'    :   'django.db.backends.postgresql_psycopg2',
        'NAME'      :   config('ACS_NAME'), 
        'USER'      :   config('ACS_USER'),
        'PASSWORD'  :   config('ACS_PASSWORD'),
        'HOST'      :   config('ACS_HOST'),
        'PORT'      :   config('ACS_PORT'),
        'TIME_ZONE' :   None,

    } 
}

STATIC_ROOT = os.path.join(BASE_DIR, "../static/")
STATIC_VERSION = 1.0

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.mailgun.org'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# EMAIL_USE_TLS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': '%(asctime)s  [%(levelname)s] %(name)s: %(message)s '},
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'debug.log',
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'django_request.log',
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {

        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
