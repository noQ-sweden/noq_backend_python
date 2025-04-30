from .common import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-l3o_ieey@d#^e-#kkk9efo7okg^fm-_q4-iq0h-=lftjnf%cn^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "noqbackend.pythonanywhere.com", "127.0.0.1:5173", "localhost:5173",'http://localhost:5173']

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Use sqlite during development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "noq.sqlite3",
    }
}
