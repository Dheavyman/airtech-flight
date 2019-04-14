import os

import django_heroku

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Celery configuration
CELERY_BROKER_URL = os.getenv('CLOUDAMQP_URL')

# Configure Django App for Heroku.
django_heroku.settings(locals())
