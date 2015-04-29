from .base import BasicActionBase
from .merge import MergeMixin
import logging

LOG = logging.getLogger(__name__)


class ExpireAction(BasicActionBase, MergeMixin):

    def execute(self, net, color_descriptor, active_tokens):
        net.expire(self.ttl_seconds)
        return []

    @property
    def ttl_seconds(self):
        return self.args['ttl_seconds']
