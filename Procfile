web: gunicorn app.app:app
worker: celery --workdir=. -A app.app:celery_app worker --loglevel=info -P eventlet
