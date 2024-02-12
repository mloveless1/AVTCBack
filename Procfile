web: gunicorn app.app:app
worker: celery -A app.tasks.celery worker --loglevel=info
