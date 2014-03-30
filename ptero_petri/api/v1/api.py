from flask import g, request
from flask.ext.restful import Resource, Api
import traceback

__all__ = ['api']


api = Api(default_mediatype='application/json')

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
            entry_links[place_name] = api.url_for(TokenListView,
                    net_key=net.key,
                    place_idx=net.named_place_indexes[place_name],
                    _external=True)
        return {'net_key': net.key, 'entry_links': entry_links}, 201

api.add_resource(NetListView, '/nets', endpoint='net-list')
api.add_resource(NetView, '/nets/<string:net_key>', endpoint='net')
api.add_resource(TokenListView,
    '/nets/<string:net_key>/places/<int:place_idx>/tokens',
    endpoint='token-list')
api.add_resource(TokenView,
    '/nets/<string:net_key>/places/<int:place_idx>/tokens/<int:color>',
    endpoint='token')
