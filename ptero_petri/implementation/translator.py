from .petri.actions.notify import NotifyAction
from .petri.future import FutureAction, FutureNet
import itertools


class Translator(object):
    def __init__(self, net_data):
        self.net_data = net_data
        self.place_to_future_place = dict()

    def get_places(self):
        result = set()
        for transition_dict in self.net_data.get('transitions', []):
            for name in ['inputs', 'outputs']:
                result.update(set(transition_dict.get(name, [])))
        return result

    def get_transitions(self):
        return self.net_data.get('transitions', [])

    def attach_places(self, future_net):
        for place_name in self.get_places():
            self.place_to_future_place[place_name] = \
                    future_net.add_place(name=place_name,
                            is_entry=place_name in self.net_data['entry_places'])

    def attach_transitions(self, future_net):
        for transition_dict in self.get_transitions():
            ft = future_net.add_basic_transition(
                    action=get_action(transition_dict))

            for input_place_name in transition_dict.get('inputs', []):
                ft.add_arc_in(self.place_to_future_place[input_place_name])

            for output_place_name in transition_dict.get('outputs', []):
                ft.add_arc_out(self.place_to_future_place[output_place_name])

    @property
    def future_net(self):
        future_net = FutureNet()

        self.attach_places(future_net)
        self.attach_transitions(future_net)

        return future_net

    @property
    def constants(self):
        return {}

    @property
    def variables(self):
        return {}


def get_action(transition_dict):
    if 'action' in transition_dict:
        action_dict = transition_dict['action']
        action_type = action_dict.pop('type')
        return FutureAction(cls=NotifyAction, **action_dict)
    else:
        return None
