from .orchestrator.messages import CreateTokenMessage
from .petri.builder import Builder
from .petri.net import Net
from .translator import Translator
import redis
import pika


EXCHANGE = 'ptero'
ROUTING_KEY = 'petri.place.create_token'


class Backend(object):
    def create_net(self, net_data):
        translator = Translator(net_data)
        future_net = translator.future_net()
        conn       = redis.Redis()
        builder    = Builder(conn)
        stored_net = builder.store(future_net, {}, {})
        return stored_net.key

    def create_token(self, net_key, place_name):
        conn = redis.Redis()

        net = Net(connection=conn, key=net_key)
        place_idx = net.named_place_indexes[place_name]
        color_group = net.add_color_group(1)

        message = CreateTokenMessage(net_key=net_key, place_idx=place_idx,
                color=color_group.begin, color_group_idx=color_group.idx)

        self._send_message(EXCHANGE, ROUTING_KEY, message.encode())

        return color_group.begin

    def cleanup(self):
        pass


    def _send_message(self, exchange, routing_key, body):
        connection = pika.BlockingConnection()
        channel = connection.channel()
        channel.confirm_delivery()
        channel.basic_publish(exchange=exchange, routing_key=routing_key,
                body=body, properties=pika.BasicProperties(content_type='application/json',
                    delivery_mode=1))
