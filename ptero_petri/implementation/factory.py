from . import backend
from .configuration.inject.initialize import initialize_injector
from . import interfaces
import redis
import os

__all__ = ['Factory']


class Factory(object):
    def __init__(self):
        self._initialized = False
        self._injector = None
        self._redis = None

    def create_backend(self):
        self._initialize()
        return backend.Backend(redis_connection=self._redis)

    def purge(self):
        self._initialize()
        self._redis.flushall()

    def _initialize(self):
        # Lazy initialize to be pre-fork friendly.
        if not self._initialized:
            self._initialized = True
            self._injector = initialize_injector()
            self._redis = self._injector.get(interfaces.IStorage)
