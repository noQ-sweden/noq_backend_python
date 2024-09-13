from .common import *
import os

SECRET_KEY = os.environ.get('SECRET_KEY')

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "noqbackend.pythonanywhere.com"]

SECURE_CROSS_ORIGIN_OPENER_POLICY = None

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "51.21.97.243", "172.26.3.179"]

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
