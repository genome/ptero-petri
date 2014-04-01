from ...container_utils import head
from .base import BarrierActionBase
from twisted.internet import defer


class JoinAction(BarrierActionBase):
    def execute(self, net, color_descriptor, active_tokens, service_interfaces):
        token = net.create_token(color=color_descriptor.group.parent_color,
            color_group_idx=color_descriptor.group.parent_color_group_idx)

        return [token], defer.succeed(None)
