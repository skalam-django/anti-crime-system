from .base import *

SERVER = 'LOCAL'

DEBUG = True
SERVICES = False
SECRET_KEY = 'nxq9s%p&_#e6fhm-(^rr3^=*ld(^@2n+eohk2wv5x-j57pz2#^'
AES128_CPIN = '8MDOFMUZYY2G2YVF3YWBIXMS61Z3LV2B'

ALLOWED_HOSTS = ['127.0.0.1', '8e144607.ngrok.io', ]

INSTALLED_APPS += [
   
]

DATABASES = {

    'default':{
            'NAME': 'acs',
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'USER': 'postgres',
            'HOST': 'localhost',
            'PASSWORD': 'admin@123',
            'TIME_ZONE': None,
        },
}

STATIC_VERSION = 1.0