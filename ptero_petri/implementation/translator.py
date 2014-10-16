from .petri.actions.convert_to_parent_color import ConvertToParentColorAction
from .petri.actions.create_color_group import CreateColorGroupAction
from .petri.actions.join import JoinAction
from .petri.actions.notify import NotifyAction
from .petri.actions.split import SplitAction
from .petri.future import FutureAction, FutureNet
import itertools


_ACTION_CLASSES = {
    'convert-to-parent-color': ConvertToParentColorAction,
    'create-color-group': CreateColorGroupAction,
    'join': JoinAction,
    'notify': NotifyAction,
    'split': SplitAction,
}


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
            transition_type = transition_dict.get('type', 'basic')
            if transition_type == 'basic':
                ft = future_net.add_basic_transition(
                        action=self.get_action(transition_dict))
            elif transition_type == 'barrier':
                ft = future_net.add_barrier_transition(
                        action=self.get_action(transition_dict))
            else:
                # XXX Should be an api error
                raise RuntimeError('Unknown transition type')

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


    def get_action(self, transition_dict):
        if 'action' in transition_dict:
            action_dict = transition_dict['action']
            response_places = self.convert_response_places(
                    action_dict.pop('response_places', {}))
            action_type = action_dict.pop('type')
            action_class = _ACTION_CLASSES[action_type]
            if action_class is None:
                return None
            return FutureAction(cls=action_class, args=action_dict,
                    response_places=response_places)
        else:
            return None

    def convert_response_places(self, response_places):
        return {k: self.place_to_future_place[v]
                for k,v in response_places.iteritems()}
