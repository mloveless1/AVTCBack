web: gunicorn app.app:app
worker: celery -A app.app.tasks.celery worker --loglevel=info
