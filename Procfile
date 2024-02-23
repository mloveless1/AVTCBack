web: gunicorn app.app:app
worker: celery -A app.app:celery_app worker --loglevel=info -P eventlet
