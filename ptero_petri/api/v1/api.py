from flask.ext.restful import Api
from . import views

__all__ = ['api']


api = Api(default_mediatype='application/json')
api.add_resource(views.NetListView, '/nets', endpoint='net-list')
api.add_resource(views.NetView, '/nets/<string:net_key>', endpoint='net')
api.add_resource(views.TokenListView,
    '/nets/<string:net_key>/places/<string:place_name>/tokens',
    endpoint='token-list')
api.add_resource(views.TokenView,
    '/nets/<string:net_key>/places/<string:place_name>/tokens/<int:color>',
    endpoint='token')
