from ..rom import get_object
import celery


__all__ = ['NotifyPlace']


class NotifyPlace(celery.Task):
    ignore_result = True

    def run(self, net_key, place_idx, color):
        from .. import storage
        net = get_object(storage.connection, net_key)
        return net.notify_place(place_idx, color=color)
