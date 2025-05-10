from .common import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-l3o_ieey@d#^e-#kkk9efo7okg^fm-_q4-iq0h-=lftjnf%cn^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http:\/\/localhost(:[0-9]+)?$",
    r"^http:\/\/127\.0\.0\.1(:[0-9]+)?$",
]
CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Use sqlite during development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "noq.sqlite3",
    }
}

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://demo.noqapp.se/login/")
