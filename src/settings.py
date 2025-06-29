"""
Django settings for src project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv() # если вы используете python-dotenv для .env файлов
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", 'django-insecure-63c+%tsle4*%#pl@afiq$vm6%h9o@#_^$(%5!x^5!#q_2t2j71')
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rental',
    'accounts',

    'guardian',
    'django_filters'
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STRIPE_SECRET_KEY = "sk_test_51R46ZQGaR6kJ96YnWf87g5JamwsmYz1JXspgncCwWOnJegAjxojGpyAsKyeqYCneBSiJ2Q2IWRU9PIu9EviXdVKy00Uty33Pc1"
STRIPE_PUBLISHABLE_KEY = "pk_test_51R46ZQGaR6kJ96Ynh3ry6fpgzjim0OqYKDNJtBbQXqtMooEiYWvI9AhtvRpufixMtHqyqgeDRpN8uVc5cDIxo2JB00uhLP822U"

ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'rental.context_processors.navbar_data',
                'rental.context_processors.filter_values',
                'rental.context_processors.api_keys_processor'
            ],
        },
    },
]

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

WSGI_APPLICATION = 'src.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("DATABASE_NAME", "piko"),
        'USER': os.environ.get("DATABASE_USER", "postgres"),
        'PASSWORD': os.environ.get("DATABASE_PASSWORD", "password"),
        'HOST': os.environ.get("DATABASE_HOST", "localhost"),
        'PORT': os.environ.get("DATABASE_PORT", "5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'accounts.UserModel'

ANONYMOUS_USER_ID = -1

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
