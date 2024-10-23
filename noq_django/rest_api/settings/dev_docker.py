from .common import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-l3o_ieey@d#^e-#kkk9efo7okg^fm-_q4-iq0h-=lftjnf%cn^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "noqbackend.pythonanywhere.com"]
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
