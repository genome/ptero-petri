from . import exit_codes
from . import interfaces
from .brokers.amqp import config
from .command_base import CommandBase
from .configuration.inject.broker import BrokerConfiguration
from .configuration.settings.injector import setting
from .util.exit import exit_process
from injector import inject
from twisted.internet import defer
import logging
import time


LOG = logging.getLogger(__name__)


@inject(broker=interfaces.IBroker,
        binding_config=setting('bindings'))
class ConfigureRabbitMQCommand(CommandBase):
    injector_modules = [
        BrokerConfiguration,
    ]


    @staticmethod
    def annotate_parser(parser):
        pass


    def _execute(self, parsed_arguments):
        deferreds = []
        deferreds.append(self._declare_exchanges())
        deferreds.append(self._declare_queues())
        dlist = defer.DeferredList(deferreds)

        _execute_deferred = defer.Deferred()
        dlist.addCallback(self._declare_bindings,
                    _execute_deferred=_execute_deferred)
        dlist.addErrback(self._exit)

        return _execute_deferred

    def _parse_config(self):
        exchanges = set()
        queues = set()
        bindings = set()

        for exchange_name, queue_bindings in self.binding_config.iteritems():
            exchanges.add(exchange_name)

            for queue_name, topics in queue_bindings.iteritems():
                queues.add(queue_name)

                for topic in topics:
                    bindings.add( (queue_name, exchange_name, topic) )

        return exchanges, queues, bindings


    def _declare_exchanges(self):
        deferreds = []
        for conf in config.get_exchange_configurations():
            LOG.debug('Declaring exchange: %s', conf)
            deferreds.append(self.broker.channel.declare_exchange(
                conf.name, arguments=conf.arguments))

        return defer.DeferredList(deferreds)

    def _declare_queues(self):
        deferreds = []
        for conf in config.get_queue_configurations():
            LOG.debug('Declaring queue: %s', conf)
            deferreds.append(self.broker.channel.declare_queue(
                conf.queue_name, arguments=conf.arguments))

        return defer.DeferredList(deferreds)

    def _declare_bindings(self, _callback, _execute_deferred):
        deferreds = []
        for conf in config.get_binding_configurations():
            LOG.debug('Binding queue: %s', conf)
            deferreds.append(self.broker.channel.bind_queue(
                conf.queue, conf.exchange, conf.topic))

        dlist = defer.DeferredList(deferreds)
        dlist.addCallback(self._wait_and_fire_deferred,
               _execute_deferred=_execute_deferred)
        dlist.addErrback(self._exit)

        return _callback

    def _wait_and_fire_deferred(self, _callback, _execute_deferred):
        # XXX Dirty workaround.  I can't tell why the bindings aren't declared
        # by the time we get here.
        time.sleep(2)
        _execute_deferred.callback(None)

    def _exit(self, error):
        LOG.critical("Unexepected error in configurerabbitmq.\n%s", error.getTraceback())
        exit_process(exit_codes.EXECUTE_FAILURE)
