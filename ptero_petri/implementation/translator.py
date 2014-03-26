from .petri.actions.notify import NotifyAction
from .petri.future import FutureAction, FutureNet
import itertools


class Translator(object):
    def __init__(self, net_data):
        self.net_data = net_data
        self.place_to_future_place = dict()

    def get_places(self):
        return set(*itertools.chain(
            itertools.chain(
                transition_dict.get('inputs', []),
                transition_dict.get('outputs', []))
            for transition_dict in self.net_data.get('transitions', [])))

    def get_transitions(self):
        return self.net_data.get('transitions', [])

    def attach_places(self, future_net):
        for place_name in self.get_places():
            self.place_to_future_place[place_name] = \
                    future_net.add_place(place_name)

    def attach_transitions(self, future_net):
        for transition_dict in self.get_transitions():
            ft = future_net.add_basic_transition(
                    action=get_action(transition_dict))

            for input_place_name in transition_dict.get('inputs', []):
                ft.add_arc_in(self.place_to_future_place[input_place_name])

            for output_place_name in transition_dict.get('outputs', []):
                ft.add_arc_out(self.place_to_future_place[output_place_name])

    def future_net(self):
        future_net = FutureNet()

        self.attach_places(future_net)
        self.attach_transitions(future_net)

        return future_net


def get_action(transition_dict):
    if 'action' in transition_dict:
        action_dict = transition_dict['action']
        action_type = action_dict.pop('type')
        return FutureAction(cls=NotifyAction, **action_dict)
    else:
        return None
