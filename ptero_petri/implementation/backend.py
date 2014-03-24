from .translator import Translator
from .builder import Builder
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
        return 1234

    def cleanup(self):
        pass
