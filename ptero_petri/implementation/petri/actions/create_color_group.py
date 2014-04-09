from ...container_utils import head
from .base import BasicActionBase
from twisted.internet import defer
import json
import os
import requests
import time


class CreateColorGroupAction(BasicActionBase):
    def execute(self, net, color_descriptor, active_tokens, service_interfaces):
        input_token = net.token(head(active_tokens))

        size = int(input_token.data['color_group_size'])
        new_color_group = net.add_color_group(size=size,
                parent_color=color_descriptor.color,
                parent_color_group_idx=color_descriptor.group.idx)

        output_token = net.create_token(color=color_descriptor.color,
                color_group_idx=color_descriptor.group.idx,
                data={'color_group_idx': new_color_group.idx})

        notify_url = self.notify_url()
        if notify_url:
            _retry(requests.put, notify_url,
                    data=self.request_body(color_descriptor.color,
                        color_descriptor.group.idx, new_color_group, net),
                    headers={'Content-Type': 'application/json'})

        return [output_token], defer.succeed(None)


    def notify_url(self):
        return self.args['url']

    def request_body(self, token_color, token_color_group_idx, new_color_group,
            net):
        data = {
            'color_group': {
                'index': new_color_group.idx,
                'color_begin': new_color_group.begin,
                'color_end': new_color_group.end,
                'parent_color': new_color_group.parent_color,
                'parent_color_group_idx': new_color_group.parent_color_group_idx,
            },
        }

        response_links = {}
        for state_name, place_idx in self.response_places.iteritems():
            response_links[state_name] = _url(net_key=net.key,
                    place_idx=place_idx, color=token_color,
                    color_group=token_color_group_idx)
        if response_links:
            data['response_links'] = response_links

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
