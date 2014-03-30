from flask import g, request, url_for
from flask.ext.restful import Resource
import traceback

class NetView(Resource):
    pass

class TokenListView(Resource):
    def post(self, net_key, place_idx):
        try:
            color = g.backend.create_token(net_key, place_idx)
        except Exception as e:
            traceback.print_exc()
            raise
        return {'color': color}, 201

class TokenView(Resource):
    pass

class NetListView(Resource):
    def post(self):
        net = g.backend.create_net(request.json)
        entry_links = {}
        for place_name in net.constant('entry_places'):
            entry_links[place_name] = url_for('token-list',
                    net_key=net.key,
                    place_idx=net.named_place_indexes[place_name],
                    _external=True)
        return {'net_key': net.key, 'entry_links': entry_links}, 201
