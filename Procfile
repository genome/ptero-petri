web: gunicorn --bind 0.0.0.0:$PTERO_PETRI_LAUNCH_PORT ptero_petri.api.wsgi:app --access-logfile - --error-logfile -
worker: celery worker -A ptero_petri.implementation.celery_app -Q worker
http_worker: celery worker -A ptero_petri.implementation.celery_app -Q http
