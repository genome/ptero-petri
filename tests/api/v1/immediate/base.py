from ...base import BaseAPITest
from ptero_petri.api import application


class ImmediateAPITest(BaseAPITest):
    def create_wsgi_app(self):
        return application.create_app({'CELERY_ALWAYS_EAGER': True})
