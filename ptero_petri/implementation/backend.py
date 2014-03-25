from .petri.builder import Builder
from .petri.net import Net
from .translator import Translator
import redis


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
        place_index = net.named_place_indexes[place_name]
        # Construct message
        # Send message (directly with kombu?)

        return 1234

    def cleanup(self):
        pass
