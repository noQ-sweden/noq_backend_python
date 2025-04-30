from .common import *
import os

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False

SERVER_IPS = os.environ.get('ALLOWED_HOSTS',"").split(",")

ALLOWED_HOSTS = ["127.0.0.1", "localhost", ] + SERVER_IPS

CORS_ALLOWED_ORIGINS = [ 
    f'http://{ip}' for ip in SERVER_IPS 
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http:\/\/localhost:*([0-9]+)?$",
]

CORS_ALLOW_CREDENTIALS = True

SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/static/'
MEDIA_URL = '/static/media/'

MEDIA_ROOT = '/vol/web/media'
STATIC_ROOT = '/vol/web/static'

FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://www.noqapp.se/")
