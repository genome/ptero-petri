from flask import request
import json
import jsonschema
import pkg_resources


def _load_schema(schema_name):
    return json.load(pkg_resources.resource_stream('ptero_petri',
                                                   _schema_path(schema_name)))


_BASE_PATH = '/'.join(__package__.split('.')[1:])


def _schema_path(schema_name):
    return '%s/schemas/%s.json' % (_BASE_PATH, schema_name)


_POST_NET_SCHEMA = _load_schema('post_net')


def get_net_post_data():
    data = request.json
    jsonschema.validate(data, _POST_NET_SCHEMA)
    return data
