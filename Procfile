web: gunicorn app.app:app
worker: celery -A app.app:celery worker --loglevel=info
