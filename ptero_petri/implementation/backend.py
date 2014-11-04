from . import exceptions
from .petri.builder import Builder
from .translator import Translator
import base64
import celery
import uuid


class Backend(object):
    def create_net(self, net_data):
        net_key = generate_net_key()

        self.submit_net.delay(net_key, net_data)

        return {'net_key': net_key}

    @property
    def submit_net(self):
        return celery.current_app.tasks[
                'ptero_petri.implementation.celery_tasks.submit_net.SubmitNet']

    @property
    def put_token(self):
        return celery.current_app.tasks[
                'ptero_petri.implementation.celery_tasks.create_token.CreateToken']

    def cleanup(self):
        pass


def generate_net_key():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2]
