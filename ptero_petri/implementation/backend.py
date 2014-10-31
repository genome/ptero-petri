from . import exceptions
from .petri.builder import Builder
from .petri.net import Net
from .translator import Translator
import celery


class Backend(object):
    def __init__(self, redis_connection):
        self.redis_connection = redis_connection

    def create_net(self, net_data):
        translator = Translator(net_data)
        builder    = Builder(self.redis_connection)
        stored_net = builder.store(translator.future_net, translator.variables,
                translator.constants)
        return {
                'net_key': stored_net.key,
                'entry_place_info': stored_net.entry_places.value
        }

    def put_token(self, net_key, place_idx, color=None, color_group_idx=None,
            data=None):
        task = celery.current_app.tasks[
                'ptero_petri.implementation.celery_tasks.create_token.CreateToken']
        task.delay(net_key, place_idx, color=color,
                color_group_idx=color_group_idx, data=data)

    def cleanup(self):
        pass
