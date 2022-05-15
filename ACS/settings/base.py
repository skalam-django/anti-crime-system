import os, os.path as path
import sys,os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'generalize',
    'acs_users',
    'gsm_rf_device',
    'main_user',
    'police_station',
    'signal_reciever',
    'notipush',
]

MIDDLEWARE = [
    'ACS.middleware.ACSPreMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ACS.middleware.ACSPostMiddleware',
]

ROOT_URLCONF = 'ACS.urls'

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

WSGI_APPLICATION = 'ACS.wsgi.application'

AUTH_USER_MODEL = "acs_users.AuthUser"

LOGIN_URL = '/login'
LOGOUT_REDIRECT_URL = '/login'

SESSION_COOKIE_AGE = 30*24*60*60 # 1 MONTH SESSION AGE

OTP =   {
            'OTP_LENGTH'    :   6,  # OTP of 6 characters
            'OTP_EXPIRY'    :   15*60, # 15 mins
            'SENDING_CONST' :   10/10, # within 10 secs 10 failure-attempts allowed
            'TIMEOUT'       :   5*1,  # secs
        'RESEND_TIMEOUT':   60*2,  # secs 
            'RESEND_CONST'  :   60,    # secs   
        }

DEFAULT_THROTTLE_RATES = {
    'anonymous'     :   [ 10, 10, 10, 15*60, 15], # 15 request per 10 secs
    'auth_user'     :   [ 20, 10 ], # 50 request per 10 secs
    'requests'      :   [ 100, 10 ], # 30 request per 10 secs
}


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



# SOCIAL_AUTH_URL_NAMESPACE = 'social'
# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '517657911626-l5oj3doogcdg971a62vr9s5scjv0p8qu.apps.googleusercontent.com'
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'IzRXylbJGfL9OrrOEc88eIlh'
# SOCIAL_AUTH_FACEBOOK_KEY = '553679145396296'        # App ID
# SOCIAL_AUTH_FACEBOOK_SECRET = '94ddf1d7d5a3d0397f10abf70416d52f'  # App Secret
# SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_link'] # add this
# SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {       # add this
#   'fields': 'id, name, email, picture.type(large), link'
# }
# SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [                 # add this
#     ('name', 'name'),
#     ('email', 'email'),
#     ('picture', 'picture'),
#     ('link', 'profile_url'),
# ]

# # REDIRECT_FIELD_NAME
# LOGOUT_REDIRECT_URL = '/'

# AUTHENTICATION_BACKENDS = [
#     # 'social_core.backends.linkedin.LinkedinOAuth2',
#     # 'social_core.backends.instagram.InstagramOAuth2',
#     'social_core.backends.facebook.FacebookOAuth2',
#     'social_core.backends.google.GoogleOAuth2',
#     'django.contrib.auth.backends.ModelBackend',
# ]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, "static/")


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', )
}



CACHE_TTL = 24*60*60
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

BROKER_URL = CACHES['default']['LOCATION']  #'redis://127.0.0.1:6379' #values.Value('redis://localhost:6379/0')
BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600,
    'fanout_prefix': True,
    'fanout_patterns': True,
}
CELERY_TASK_SERIALIZER      =   'json' #'pickle'
CELERY_RESULT_SERIALIZER    =   'json' #'pickle'
CELERY_RESULT_BACKEND       =   CACHES['default']['LOCATION'] #'redis://127.0.0.1:6379'  #values.Value('redis')
CELERY_TASK_RESULT_EXPIRES  =   3600
CELERY_ACCEPT_CONTENT       =   ['pickle', 'application/json', 'msgpack', 'yaml']
CELERY_DISABLE_RATE_LIMITS  =   True
CELERY_CHORD_PROPAGATES     =   True
# CELERY_ALWAYS_EAGER = False
# CELERY_DEFAULT_QUEUE = values.Value('celery', environ_name='QUEUE_NAME')
CELERY_TIMEZONE             =   'Asia/Kolkata'
USE_TZ                      =   False


DEVICE_ID_LEN = 6
REQUEST_ID_LEN = 6

CLIENT_GROUPS  = (
                    ('mu','Main User'),
                    ('mud','Main User Device'),
                    ('grft','GSM-RF Tower'),
                    ('ps', 'Police Station'),
                )


NOTIPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY"      :   "BDPXgINzfT7Lbb-FIaiMAVD-tsB3cix5K4osVk5MCAn8hVpt8S-tfMGBUXKx4gpArUrwpdVHYoJavF7za4uMW34",
    "VAPID_PRIVATE_KEY"     :   "hjrKA7tPz9AxgNijGwwSPNBFNJfPb6-QnpNxziMxN2Q",
    "VAPID_ADMIN_EMAIL"     :   "alam@futretailtech.in",
}

MEDIA_ROOT  = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'



PHONENUMBER_DB_FORMAT = 'E164'
PHONENUMBER_DEFAULT_FORMAT = 'E164'
PHONENUMBER_DEFAULT_REGION = 'IN'


GSMRFT_ALARM_URL    =   '/alarm/'
GSMRFT_VIA_URL      =   '/via/'
MUD_HELP_URL        =   '/help/'
MUD_VIA_URL         =   '/via/'