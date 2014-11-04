from flask import g, request
from flask.ext.restful import Resource
import base64
import uuid


class NetView(Resource):
    def put(self, net_key):
        return _submit_net(net_key)


class TokenListView(Resource):
    def post(self, net_key, place_idx):
        color = g.backend.put_token.delay(net_key, place_idx)
        return {}, 201

    def put(self, net_key, place_idx):
        color_group_idx = int(request.args['color_group'])
        color = int(request.args['color'])

        g.backend.put_token.delay(net_key=net_key, place_idx=place_idx,
                color=color, color_group_idx=color_group_idx,
                data=request.json)

        return {}, 201


class NetListView(Resource):
    def post(self):
        net_key = _generate_net_key()
        return _submit_net(net_key)


def _submit_net(net_key):
    net_data = request.json

    net_info = g.backend.create_net(net_data, net_key=net_key)

    return net_info, 201


def _generate_net_key():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2]
