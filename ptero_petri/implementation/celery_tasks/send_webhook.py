import celery
import json
import logging
from ptero_common.logging_configuration import logged_request


LOG = logging.getLogger(__name__)


__all__ = ['SendWebhookTask']


class SendWebhookTask(celery.Task):
    ignore_result = True

    def run(self, url, **kwargs):
        logged_request.put(
            url, data=self.body(kwargs),
            headers={'Content-Type': 'application/json'}, logger=LOG)

    def body(self, kwargs):
        return json.dumps(kwargs)
