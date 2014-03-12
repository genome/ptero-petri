from flask.ext.restful import Api
from . import views

__all__ = ['api']


api = Api(default_mediatype='application/json')
api.add_resource(views.NetListView, '/nets', endpoint='net-list')
api.add_resource(views.NetView, '/nets/<string:pk>', endpoint='net')
