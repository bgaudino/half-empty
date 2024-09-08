from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['half-empty.fly.dev']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True
SERVER_EMAIL = DEFAULT_FROM_EMAIL = CONTACT_EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SITE_URL = 'https://half-empty.fly.dev'
