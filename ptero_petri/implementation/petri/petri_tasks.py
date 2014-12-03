import celery
import logging


LOG = logging.getLogger(__name__)


def execute_task(name, *args, **kwargs):
    LOG.debug('Execute task: %s, %s, %s', name, args, kwargs)
    task = celery.current_app.tasks[_full_task_name(name)]
    task.delay(*args, **kwargs)


_BASE_PATH = 'ptero_petri.implementation.celery_tasks.'
_REGISTERED_TASKS = {
    'NotifyTransition': _BASE_PATH + 'notify_transition.NotifyTransition',
    'NotifyPlace': _BASE_PATH + 'notify_place.NotifyPlace',
}


def _full_task_name(name):
    return _REGISTERED_TASKS[name]
