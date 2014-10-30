from .. import celery_app
import os


__all__ = ['send_webhook']


HTTP_TASK = 'ptero_petri.implementation.celery_tasks.http_callback.HTTPCallbackTask'


def send_webhook(url, response_data=None, data=None):
    body_data = dict(data)
    body_data['response_links'] = _response_links(**response_data)
    task = celery_app.app.tasks[HTTP_TASK]

    task.delay(url, **body_data)


def _response_links(net_key, response_places, color_descriptor):
    response_links = {}
    for state_name, place_idx in response_places.iteritems():
        response_links[state_name] = _url(net_key=net_key,
                place_idx=place_idx, color=color_descriptor.color,
                color_group_idx=color_descriptor.group.idx)
    return response_links


def _url(net_key, place_idx, color, color_group_idx):
    host = os.environ.get('PTERO_PETRI_HOST', 'localhost')
    port = int(os.environ.get('PTERO_PETRI_PORT', '5000'))
    return "http://%s:%d/v1/nets/%s/places/%d/tokens?color=%d&color_group=%d" % (
            host, port, net_key, place_idx, color, color_group_idx)
