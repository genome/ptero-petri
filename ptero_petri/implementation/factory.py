from . import backend
import redis
import os

__all__ = ['Factory']


class Factory(object):
    def __init__(self):
        self._initialized = False
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
            self._redis = self._create_redis_connection()

    def _create_redis_connection(self):
        return redis.Redis(
                host=os.environ.get('PTERO_PETRI_REDIS_HOST', 'localhost'),
                port=int(os.environ.get('PTERO_PETRI_REDIS_PORT', '6379')))
