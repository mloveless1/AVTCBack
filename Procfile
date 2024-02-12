web: gunicorn app.app:app
worker: celery -A app.celery worker --loglevel=info
