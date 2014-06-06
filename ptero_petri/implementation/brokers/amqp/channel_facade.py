from . import config
from injector import inject
from twisted.internet import defer
from .connection_manager import ConnectionManager
from .publisher_confirm_manager import PublisherConfirmManager
from ...util.defer import add_callback_and_default_errback
import logging
import pika


LOG = logging.getLogger(__name__)


@inject(connection_manager=ConnectionManager)
class ChannelFacade(object):
    def __init__(self):
        self._publish_properties = pika.BasicProperties(delivery_mode=2)

        self._pika_channel = None
        self._publisher_confirm_manager = None
        self._last_publish_tag = 0

    def connect(self):
        connect_deferred = self.connection_manager.connect()

        ready_deferred = defer.Deferred()
        add_callback_and_default_errback(connect_deferred, self._on_connected,
                ready_deferred)
        return ready_deferred

    def _on_connected(self, pika_channel, ready_deferred):
        if self._pika_channel is None:
            self._pika_channel = pika_channel
            self._publisher_confirm_manager = PublisherConfirmManager(
                    self._pika_channel)

            self._declare_queues_exchanges_and_bindings(ready_deferred)

        else:
            ready_deferred.callback(pika_channel)

        return pika_channel

    def _declare_queues_exchanges_and_bindings(self, deferred):
        qx_deferred = self._declare_queues_and_exchanges()
        add_callback_and_default_errback(qx_deferred,
                self._declare_bindings, done_deferred=deferred)

    def _declare_queues_and_exchanges(self):
        deferreds = []
        for conf in config.get_exchange_configurations():
            LOG.debug('Declaring exchange: %s', conf)
            deferreds.append(self._pika_channel.exchange_declare(
                exchange=conf.name, **conf.kwargs))

        for conf in config.get_queue_configurations():
            LOG.debug('Declaring queue: %s', conf)
            deferreds.append(self._pika_channel.queue_declare(
                queue=conf.queue_name, **conf.kwargs))

        return defer.DeferredList(deferreds)


    def _declare_bindings(self, qx_declare_result, done_deferred=None):
        deferreds = []
        for conf in config.get_binding_configurations():
            LOG.debug('Binding queue: %s', conf)
            deferreds.append(self._pika_channel.queue_bind(queue=conf.queue,
                exchange=conf.exchange, routing_key=conf.topic))

        dlist = defer.DeferredList(deferreds)
        add_callback_and_default_errback(dlist, self._done_declaring,
                done_deferred=done_deferred)

    def _done_declaring(self, result, done_deferred):
        done_deferred.callback(self._pika_channel)


    def bind_queue(self, queue_name, exchange_name, topic, **properties):
        return self._connect_and_do('queue_bind', queue=queue_name,
                exchange=exchange_name, routing_key=topic, **properties)

    def declare_queue(self, queue_name, durable=True, **other_properties):
        return self._connect_and_do('queue_declare', queue=queue_name,
                durable=durable, **other_properties)

    def declare_exchange(self, exchange_name, exchange_type='topic',
            durable=True, **other_properties):
        return self._connect_and_do('exchange_declare', exchange=exchange_name,
                durable=durable, exchange_type=exchange_type,
                **other_properties)

    def basic_publish(self, exchange_name, routing_key, encoded_message):
        connect_deferred = self.connect()
        confirm_deferred = defer.Deferred()
        connect_deferred.addCallback(self._basic_publish,
                confirm_deferred=confirm_deferred, exchange_name=exchange_name,
                routing_key=routing_key, encoded_message=encoded_message)
        return confirm_deferred

    def _basic_publish(self, _, confirm_deferred, exchange_name, routing_key,
            encoded_message):
        self._last_publish_tag += 1
        self._pika_channel.basic_publish(exchange=exchange_name,
                routing_key=routing_key,
                body=encoded_message,
                properties=self._publish_properties)
        self._publisher_confirm_manager.add_confirm_deferred(self._last_publish_tag,
                confirm_deferred)

    def basic_consume(self, *args, **kwargs):
        return self._pika_channel.basic_consume(*args, **kwargs)

    def basic_ack(self, recieve_tag):
        return self._pika_channel.basic_ack(recieve_tag)

    def basic_reject(self, recieve_tag, requeue=False):
        return self._pika_channel.basic_reject(recieve_tag, requeue=requeue)

    def _connect_and_do(self, fn_name, *args, **kwargs):
        if self._pika_channel is None:
            connect_deferred = self.connect()

            deferred = defer.Deferred()
            LOG.debug("Setting deferred to callback %s", fn_name)
            add_callback_and_default_errback(connect_deferred,
                    self._do_on_channel, fn_name=fn_name, args=args,
                    kwargs=kwargs, deferred=deferred)
        else:
            channel_fn = getattr(self._pika_channel, fn_name)
            LOG.debug("Immediately Executing %s", fn_name)
            deferred = channel_fn(*args, **kwargs)
        return deferred

    @staticmethod
    def _do_on_channel(pika_channel, fn_name, args, kwargs, deferred):
        LOG.debug("Executing %s", fn_name)
        channel_fn = getattr(pika_channel, fn_name)
        this_things_deferred = channel_fn(*args, **kwargs)
        this_things_deferred.chainDeferred(deferred)
        return pika_channel
