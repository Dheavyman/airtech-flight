"""
WSGI config for api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv()

if os.getenv('DJANGO_ENV') == 'production':
    settings = 'api.settings.production'
else:
    settings = 'api.settings.development'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)

application = get_wsgi_application()
