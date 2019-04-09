import os

from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
if os.getenv('DJANGO_ENV') == 'production':
    api_settings = 'api.settings.production'
else:
    api_settings = 'api.settings.development'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', api_settings)

app = Celery('api')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
