from ... import interfaces
from ...brokers.amqp_broker import AmqpBroker
import injector


class BrokerConfiguration(injector.Module):
    @injector.singleton
    @injector.provides(interfaces.IBroker)
    def provide_broker(self):
        return self.__injector__.get(AmqpBroker)
