from ..rom import get_object
import celery


class StorageMixin(object):
    def get_net(self, net_key):
        return get_object(self.storage, net_key)

    @property
    def storage(self):
        return celery.current_app.storage
