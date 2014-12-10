import celery
import requests
import json


__all__ = ['SendWebhookTask']


class SendWebhookTask(celery.Task):
    ignore_result = True

    def run(self, url, **kwargs):
        requests.put(url, data=self.body(kwargs),
                     headers={'Content-Type': 'application/json'})

    def body(self, kwargs):
        return json.dumps(kwargs)
