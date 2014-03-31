from ...container_utils import head
from .base import BasicActionBase
from twisted.internet import defer
import requests
import time

class NotifyAction(BasicActionBase):

    def execute(self, net, color_descriptor, active_tokens, service_interfaces):
        new_token_idx = head(active_tokens)
        new_token = net.token(new_token_idx)
        _retry(requests.put, self.notify_url(), {})
        return [new_token], defer.succeed(None)

    def notify_url(self):
        return self.args['url']

_MAX_RETRIES = 5
_RETRY_DELAY = 0.1
def _retry(func, *args, **kwargs):
    for attempt in xrange(_MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except:
            time.sleep(_RETRY_DELAY)
    error_msg = "Failed (%s) with args (%s) and kwargs (%s) %d times" % (
            func.__name__, args, kwargs, _MAX_RETRIES)
    raise RuntimeError(error_msg)
