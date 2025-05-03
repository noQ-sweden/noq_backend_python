from .common import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-l3o_ieey@d#^e-#kkk9efo7okg^fm-_q4-iq0h-=lftjnf%cn^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True



 
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React default port
    "http://localhost:8080",  # Vue default port
    "http://localhost:4200",  # Angular default port
]

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "noqbackend.pythonanywhere.com"]

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Use sqlite during development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "noq.sqlite3",
    }
}

# Add CORS middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add corsheaders to INSTALLED_APPS
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_extensions',
    'django.contrib.staticfiles',
    'rest_api',
    'backend',
    # 'rest_framework',
    # 'rest_framework.authtoken',
]

 
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.TokenAuthentication',
#     ],
# }
    