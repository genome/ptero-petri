from . import celery_tasks  # nopep8
from . import storage
from celery.signals import worker_init, setup_logging
from ptero_common.logging_configuration import configure_celery_logging
from ptero_common.celery.utils import get_config_from_env
import celery


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

config = get_config_from_env('PETRI')
app.conf.update(config)


@setup_logging.connect
def setup_celery_logging(**kwargs):
    configure_celery_logging('PETRI')


@worker_init.connect
def initialize_sqlalchemy_session(**kwargs):
    app.storage = storage.get_connection()
