from . import celery_tasks
from . import storage
from celery.signals import worker_init
import celery
import os


app = celery.Celery('PTero-petri-celery',
        include='ptero_petri.implementation.celery_tasks')


_DEFAULT_CELERY_CONFIG = {
    'CELERY_BROKER_URL': 'amqp://localhost',
    'CELERY_RESULT_BACKEND': 'redis://localhost',
    'CELERY_ACCEPT_CONTENT': ['json'],
    'CELERY_ACKS_LATE': True,
    'CELERY_RESULT_SERIALIZER': 'json',
    'CELERY_TASK_SERIALIZER': 'json',
    'CELERYD_PREFETCH_MULTIPLIER': 10,
}
for var, default in _DEFAULT_CELERY_CONFIG.iteritems():
    if var in os.environ:
        app.conf[var] = os.environ[var]
    else:
        app.conf[var] = default

@worker_init.connect
def initialize_sqlalchemy_session(signal, sender):
    app.storage = storage.get_connection()
