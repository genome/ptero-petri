from . import v1
from ..implementation.factory import Factory
import flask


__all__ = ['create_app']


def create_app():
    factory = Factory()

    app = _create_app_from_blueprints()
    app.config['RESTFUL_JSON'] = {
            'indent': 4,
            'sort_keys': True,
    }

    _attach_factory_to_app(factory, app)

    return app


def _create_app_from_blueprints():
    app = flask.Flask('PTero Petri Service')
    app.register_blueprint(v1.blueprint, url_prefix='/v1')

    return app


def _attach_factory_to_app(factory, app):
    @app.before_request
    def before_request():
        try:
            flask.g.backend = factory.create_backend()
        except:
            LOG.exception("Exception occured while creating backend")
            return jsonify({"error": "Internal Server Error: could not create backend"}), 500

    @app.teardown_request
    def teardown_request(exception):
        if hasattr(flask.g, 'backend'):
            flask.g.backend.cleanup()
