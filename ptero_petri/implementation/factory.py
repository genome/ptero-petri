from ptero_common.factories.celeryfactorymixin import CeleryFactoryMixin
from ptero_petri.implementation import backend


__all__ = ['Factory']


class Factory(CeleryFactoryMixin):

    def __init__(self, celery_app=None):
        CeleryFactoryMixin.__init__(self, celery_app)
        self._initialized = False

    def create_backend(self):
        self._initialize()
        return backend.Backend()

    def _initialize(self):
        # Lazy initialize to be pre-fork friendly.
        if not self._initialized:
            self._initialized = True
            self._initialize_celery()

    def _initialize_celery(self):
        if self.celery_app is None:
            from ptero_petri.implementation.celery_app import app
            self.celery_app = app
