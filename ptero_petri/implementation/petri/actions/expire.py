from .base import BasicActionBase
import logging

LOG = logging.getLogger(__name__)


class ExpireAction(BasicActionBase):

    def execute(self, net, color_descriptor, active_tokens):
        net.expire(self.ttl_seconds)
        # Don't return any tokens, because returning tokens after expiring the
        # net creates new Redis keys that won't expire.
        return []

    @property
    def ttl_seconds(self):
        return self.args['ttl_seconds']
