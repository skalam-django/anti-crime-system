from .base import *
from decouple import config

SERVER = 'DEVELOPEMENT'

DEBUG = True
SECRET_KEY = config('ACS_SECRET_KEY') # '=xq4e*ltvt%&)c8=(s64eo23wj^^!=w61isrpwc3#r9(7qieqp'
SERVICES = config('ACS_SERVICES')
AES128_CPIN = config('ACS_AES128_CPIN') #'8MDOFMUZYY2G2YVF3YWBIXMS61Z3LV2B'  # 32 characters

ALLOWED_HOSTS = [
                    '127.0.0.1',
                    'c2fd68bb.ngrok.io',
                ]

INSTALLED_APPS += [
   
]

STATIC_VERSION = 1.0

DATABASES = {
    'default':{
            'NAME': config('ACS_NAME'),
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'USER': config('ACS_USER'),
            'HOST': config('ACS_HOST'),
            'PASSWORD': config('ACS_PASSWORD'),
            'TIME_ZONE': None,
        },
}

STATIC_VERSION = 1.0

# SECURE_SSL_REDIRECT             =   True
# SECURE_PROXY_SSL_HEADER         =   ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_EXPIRE_AT_BROWSER_CLOSE =   False
# CSRF_COOKIE_SECURE              =   True
# SESSION_COOKIE_SECURE           =   True
# SECURE_HSTS_SECONDS             =   100000
# SECURE_HSTS_INCLUDE_SUBDOMAINS  =   True
# SECURE_HSTS_PRELOAD             =   True
# SECURE_REDIRECT_EXEMPT          =   ["^insecure/"]

# SECURE_BROWSER_XSS_FILTER       =   True
# SECURE_CONTENT_TYPE_NOSNIFF     =   True
# X_FRAME_OPTIONS                 =   'DENY'
# SECURE_REFERRER_POLICY          =   'same-origin'