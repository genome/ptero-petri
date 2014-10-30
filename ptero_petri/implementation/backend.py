from . import exceptions
from .petri.builder import Builder
from .petri.net import Net
from .translator import Translator


EXCHANGE = 'ptero'
ROUTING_KEY = 'petri.place.create_token'


class Backend(object):
    def __init__(self, redis_connection):
        self.redis_connection = redis_connection

    def create_net(self, net_data):
        translator = Translator(net_data)
        builder    = Builder(self.redis_connection)
        stored_net = builder.store(translator.future_net, translator.variables,
                translator.constants)
        return {
                'net_key':stored_net.key,
                'entry_place_info': stored_net.entry_places.value
        }

    def create_token(self, net_key, place_idx):
        net = Net(connection=self.redis_connection, key=net_key)
        self._validate_place_idx(net, place_idx)

        color_group = net.add_color_group(1)
        net.create_put_notify(place_idx, color=color_group.begin,
                color_group_idx=color_group.idx)

        return color_group.begin

    def put_token(self, net_key, place_idx, color_group_idx, color, data=None):
        net = Net(connection=self.redis_connection, key=net_key)
        self._validate_place_idx(net, place_idx)
        self._validate_color_in_color_group(net, color, color_group_idx)
        net.create_put_notify(place_idx=place_idx, color=color,
                color_group_idx=color_group_idx, data=data)

    def _validate_place_idx(self, net, place_idx):
        if not place_idx < net.num_places:
            raise exceptions.InvalidPlace(
                    'Invalid place index (%d) given for net (%s).'
                    % (place_idx, net.key))

    def _validate_color_in_color_group(self, net, color, color_group_idx):
        color_group = net.color_group(color_group_idx)
        if not (color >= color_group.begin and color < color_group.end):
            raise exceptions.InvalidColor(
                    'Invalid color (%d) + color_group (%d) for net (%s).'
                    % (color, color_group_idx, net.key))

    def cleanup(self):
        pass
