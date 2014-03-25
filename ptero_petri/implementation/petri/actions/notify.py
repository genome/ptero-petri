from ...container_utils import head
from .base import BasicActionBase
from twisted.internet import defer
import requests

class NotifyAction(BasicActionBase):

    def execute(self, net, color_descriptor, active_tokens, service_interfaces):
        new_token_idx = head(active_tokens)
        new_token = net.token(new_token_idx)
        requests.put(self.notify_url(), {})
        return [new_token], defer.succeed(None)

    def notify_url(self):
        return self.args['url']
