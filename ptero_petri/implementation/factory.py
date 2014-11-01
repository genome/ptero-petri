from . import backend


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
            self._initialize_storage()
            self._initialize_celery()

    def _initialize_storage(self):
        from . import storage
        self._redis = storage.connection

    def _initialize_celery(self):
        from . import celery_app
