from ..rom import get_object
import celery


__all__ = ['NotifyTransition']


class NotifyTransition(celery.Task):
    ignore_result = True

    def run(self, net_key, place_idx, transition_idx, token_idx):
        from .. import storage
        net = get_object(storage.connection, net_key)
        net.notify_transition(transition_idx, place_idx, token_idx)
