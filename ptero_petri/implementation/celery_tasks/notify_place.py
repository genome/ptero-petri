from .storage_mixin import StorageMixin
import celery


__all__ = ['NotifyPlace']


class NotifyPlace(celery.Task, StorageMixin):
    ignore_result = True

    def run(self, net_key, place_idx, color):
        net = self.get_net(net_key)
        net.notify_place(place_idx, color=color)
