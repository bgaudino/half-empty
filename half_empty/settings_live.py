from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['half-empty.fly.dev']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
