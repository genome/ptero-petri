from flask.ext.restful import Api
from . import views

__all__ = ['api']


api = Api(default_mediatype='application/json')

api.add_resource(views.NetListView, '/nets', endpoint='net-list')
api.add_resource(views.NetView, '/nets/<string:net_key>', endpoint='net')
api.add_resource(views.TokenListView,
                 '/nets/<string:net_key>/places/<int:place_idx>/tokens',
                 endpoint='token-list')

api.add_resource(views.ServerInfo, '/server-info', endpoint='server-info')
