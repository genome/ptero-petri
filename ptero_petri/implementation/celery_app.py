from . import celery_tasks  # nopep8
from . import storage
from celery.signals import worker_init, setup_logging
from ptero_common.logging_configuration import configure_celery_logging
import celery
import os


TASK_PATH = 'ptero_petri.implementation.celery_tasks'

app = celery.Celery('PTero-petri-celery', include=TASK_PATH)

app.conf['CELERY_ROUTES'] = (
    {
        TASK_PATH + '.create_token.CreateToken': {'queue': 'worker'},
        TASK_PATH + '.notify_place.NotifyPlace': {'queue': 'worker'},
        TASK_PATH + '.notify_transition.NotifyTransition': {'queue': 'worker'},
        TASK_PATH + '.submit_net.SubmitNet': {'queue': 'worker'},
        'ptero_common.celery.http.HTTP': {'queue': 'http'},
    },
)

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


@setup_logging.connect
def setup_celery_logging(**kwargs):
    configure_celery_logging('PETRI')


@worker_init.connect
def initialize_sqlalchemy_session(**kwargs):
    app.storage = storage.get_connection()
