from .storage_mixin import StorageMixin
from ..petri.builder import Builder
from ..translator import Translator
import celery


__all__ = ['SubmitNet']


class SubmitNet(celery.Task, StorageMixin):
    ignore_result = True

    def run(self, net_key, net_data):
        net_data['entry_places'] = set(net_data.get('entry_places', []))
        net_data['initialMarking'] = set(net_data.get('initialMarking', []))

        translator = Translator(net_data)
        builder = Builder(self.storage)
        stored_net = builder.store(translator.future_net, translator.variables,
                                   translator.constants, net_key=net_key)

        color_group = stored_net.add_color_group(1)

        self._place_initial_tokens(stored_net.key,
                                   net_data.get('initialMarking'),
                                   color=color_group.begin,
                                   color_group_idx=color_group.idx)

    def _place_initial_tokens(self, net_key, initial_marking, color,
                              color_group_idx):
        for place_name in initial_marking:
            self.put_token.delay(net_key, place_name=place_name,
                                 color=color, color_group_idx=color_group_idx)

    @property
    def put_token(self):
        return celery.current_app.tasks[
            'ptero_petri.implementation.celery_tasks.create_token.CreateToken']
