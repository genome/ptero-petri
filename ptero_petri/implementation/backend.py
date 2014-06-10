from . import exceptions
from .orchestrator.messages import CreateTokenMessage
from .petri.builder import Builder
from .petri.net import Net
from .translator import Translator
import pika


EXCHANGE = 'ptero'
ROUTING_KEY = 'petri.place.create_token'


class Backend(object):
    def __init__(self, redis_connection, amqp_parameters):
        self.redis_connection = redis_connection
        self.amqp_parameters = amqp_parameters

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
        color_group = net.add_color_group(1)

        self.put_token(net_key, place_idx, color_group_idx=color_group.idx,
                color=color_group.begin)

        return color_group.begin

    def put_token(self, net_key, place_idx, color_group_idx, color, data=None):
        self._validate_place_idx(net_key, place_idx)
        self._validate_color_in_color_group(net_key, color, color_group_idx)

        message = CreateTokenMessage(net_key=net_key, place_idx=place_idx,
                color=color, color_group_idx=color_group_idx, data=data)

        self._send_message(EXCHANGE, ROUTING_KEY, message.encode())

    def _validate_place_idx(self, net_key, place_idx):
        net = Net(connection=self.redis_connection, key=net_key)
        if not place_idx < net.num_places:
            raise exceptions.InvalidPlace(
                    'Invalid place index (%d) given for net (%s).'
                    % (place_idx, net.key))

    def _validate_color_in_color_group(self, net_key, color, color_group_idx):
        net = Net(connection=self.redis_connection, key=net_key)
        color_group = net.color_group(color_group_idx)
        if not (color >= color_group.begin and color < color_group.end):
            raise exceptions.InvalidColor(
                    'Invalid color (%d) + color_group (%d) for net (%s).'
                    % (color, color_group_idx, net.key))

    def cleanup(self):
        pass


    def _send_message(self, exchange, routing_key, body):
        connection = pika.BlockingConnection()
        channel = connection.channel()
        channel.confirm_delivery()
        channel.basic_publish(exchange=exchange, routing_key=routing_key,
                body=body, properties=pika.BasicProperties(content_type='application/json',
                    delivery_mode=1))
