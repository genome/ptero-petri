web: gunicorn ptero_petri.api.wsgi:app --access-logfile - --error-logfile -
worker: celery worker --loglevel=INFO -A ptero_petri.implementation.celery_app
