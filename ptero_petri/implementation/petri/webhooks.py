import os
import requests
import simplejson
import time


__all__ = ['send_webhook']


def send_webhook(url, response_data=None, data=None):

    _retry(requests.put, url,
            data=_request_body(
                response_links=_response_links(**response_data),
                data=data),
            headers={'Content-Type': 'application/json'})


def _response_links(net_key, response_places, color_descriptor):
    response_links = {}
    for state_name, place_idx in response_places.iteritems():
        response_links[state_name] = _url(net_key=net_key,
                place_idx=place_idx, color=color_descriptor.color,
                color_group_idx=color_descriptor.group.idx)
    return response_links


def _request_body(response_links, data):
    body_data = dict(data)
    body_data['response_links'] = response_links

    return simplejson.dumps(body_data)


def _url(net_key, place_idx, color, color_group_idx):
    host = os.environ.get('PTERO_PETRI_HOST', 'localhost')
    port = int(os.environ.get('PTERO_PETRI_PORT', '5000'))
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
