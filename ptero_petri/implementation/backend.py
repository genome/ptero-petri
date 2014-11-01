from . import exceptions
from .petri.builder import Builder
from .translator import Translator
import base64
import celery
import uuid


class Backend(object):
    def __init__(self, redis_connection):
        self.redis_connection = redis_connection

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

    def _place_initial_tokens(self, net_key, initial_marking):
        for place_name in initial_marking:
            self.put_token.delay(net_key, place_name=place_name)

    def cleanup(self):
        pass


def generate_net_key():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2]
