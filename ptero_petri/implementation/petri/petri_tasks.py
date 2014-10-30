from .. import celery_app
from .. import celery_tasks
import logging


LOG = logging.getLogger(__name__)


def execute_task(name, *args, **kwargs):
    LOG.debug('Execute task: %s, %s, %s', name, args, kwargs)
    task = celery_app.app.tasks[_full_task_name(name)]
    task.delay(*args, **kwargs)


def _full_task_name(name):
    task_class = getattr(celery_tasks, name)
    return task_class.name
