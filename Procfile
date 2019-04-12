release: python manage.py migrate
web: gunicorn api.wsgi --log-file -
mainworker: celery -A api worker -B -l info
