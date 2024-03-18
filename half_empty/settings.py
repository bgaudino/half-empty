import os
from pathlib import Path

from django.contrib import messages

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'authtools',

    'accounts',
    'core',
    'todos',
    'quotes',

    'django.forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'csp.middleware.CSPMiddleware',

    'core.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'half_empty.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Path(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'quotes.context_processors.quote',
            ],
        },
    },
]

WSGI_APPLICATION = 'half_empty.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default='postgres:///half_empty')
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

LOGOUT_REDIRECT_URL = '/accounts/login/'

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'infofmation',
    messages.SUCCESS: 'positive',
    messages.WARNING: 'warning',
    messages.ERROR: 'negative',
}

FORM_RENDERER = 'core.forms.VanillaFormRenderer'

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SITE_URL = 'http://localhost:8000'

RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')

CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL')

CSP_STYLE_SRC = (
    "'self'",
    'https://assets.ubuntu.com/v1/vanilla-framework-version-4.6.0.min.css',
    # htmx
    "'sha256-pgn1TCGZX6O77zDvy0oTODMOxemn0oj0LeCnQTRj7Kg='",
    # sweetalert
    "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='",
    "'sha256-UQBytKn0DQWyDg5/YC+FaQxonSsbQk4k0ErDHqBuhfw='",
)
CSP_IMG_SRC = ("'self'", 'data:',)
CSP_FONT_SRC = ('https://assets.ubuntu.com/v1/',)
CSP_INCLUDE_NONCE_IN = ('script-src',)
CSP_SCRIPT_SRC = (
    "'self'",
    'https://cdn.jsdelivr.net/npm/sweetalert2@11.10.6/dist/sweetalert2.all.min.js',
    'https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js',
    'https://www.google.com/recaptcha/api.js',
)
