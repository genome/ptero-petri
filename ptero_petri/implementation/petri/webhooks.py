import json
import os
import requests
import time


__all__ = ['send_webhook']


def send_webhook(url, net_key, response_places, color_descriptor, data=None):
    _retry(requests.put, url,
            data=_request_body(net_key, response_places, color_descriptor,
                additional_data=data),
            headers={'Content-Type': 'application/json'})


def _request_body(net_key, response_places, color_descriptor, additional_data):
    response_links = {}
    for state_name, place_idx in response_places.iteritems():
        response_links[state_name] = _url(net_key=net_key,
                place_idx=place_idx, color=color_descriptor.color,
                color_group_idx=color_descriptor.group.idx)

    color_group = color_descriptor.group
    data = {
        'token_color': color_descriptor.color,
        'color_group': {
            'index': color_group.idx,
            'color_begin': color_group.begin,
            'color_end': color_group.end,
            'parent_color': color_group.parent_color,
            'parent_color_group_index': color_group.parent_color_group_idx,
        },
        'response_links': response_links,
    }

    if additional_data:
        data.update(additional_data)

    return json.dumps(data)


def _url(net_key, place_idx, color, color_group_idx):
    host = os.environ.get('PETRI_HOST', 'localhost')
    port = int(os.environ.get('PETRI_PORT', '5000'))
    return "http://%s:%d/v1/nets/%s/places/%d/tokens?color=%d&color_group=%d" % (
            host, port, net_key, place_idx, color, color_group_idx)


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
