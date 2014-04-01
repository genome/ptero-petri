from ...container_utils import head
from .base import BasicActionBase
from twisted.internet import defer
import os
import json
import requests
import time

class NotifyAction(BasicActionBase):

    def execute(self, net, color_descriptor, active_tokens, service_interfaces):
        new_token_idx = head(active_tokens)
        new_token = net.token(new_token_idx)

        _retry(requests.put, self.notify_url(),
                data=self.request_body(new_token, net),
                headers={'Content-Type': 'application/json'})

        return [new_token], defer.succeed(None)

    def notify_url(self):
        return self.args['url']

    def request_body(self, token, net):
        response_links = {}
        for state_name, place_idx in self.response_places.iteritems():
            response_links[state_name] = _url(net_key=net.key,
                    place_idx=place_idx, color=token.color.value,
                    color_group=token.color_group_idx.value)

        data = {
            'token': token.as_dict,
            'response_links': response_links,
        }
        if 'requested_data' in self.args:
            data['requested_data'] = self.args['requested_data']

        return json.dumps(data)


def _url(net_key, place_idx, color, color_group):
    host = os.environ.get('PETRI_HOST', 'localhost')
    port = int(os.environ.get('PETRI_PORT', '5000'))
    return "http://%s:%d/v1/nets/%s/places/%d/tokens?color=%d&color_group=%d" % (
            host, port, net_key, place_idx, color, color_group)


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
