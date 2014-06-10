from . import backend
from . import interfaces
from .brokers.amqp.connection_manager import ConnectionParams
from .configuration.inject.initialize import initialize_injector
import redis
import os

__all__ = ['Factory']


class Factory(object):
    def __init__(self):
        self._initialized = False
        self._injector = None
        self._redis = None
        self._connection_parameters = None

    def create_backend(self):
        self._initialize()
        return backend.Backend(redis_connection=self._redis,
                amqp_parameters=self._connection_parameters)

    def purge(self):
        self._initialize()
        self._redis.flushall()

    def _initialize(self):
        # Lazy initialize to be pre-fork friendly.
        if not self._initialized:
            self._initialized = True
            self._injector = initialize_injector()
            self._redis = self._injector.get(interfaces.IStorage)
            self._connection_parameters = self._injector.get(ConnectionParams)
