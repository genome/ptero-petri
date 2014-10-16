from .base import BasicActionBase
from .merge import MergeMixin
from twisted.internet import defer


class ConvertToParentColorAction(BasicActionBase, MergeMixin):
    def execute(self, net, color_descriptor, active_tokens, service_interfaces):
        new_token = net.create_token(
                color=color_descriptor.group.parent_color,
                color_group_idx=color_descriptor.group.parent_color_group_idx)
        self.merge_data(net, new_token, active_tokens)

        return [new_token], defer.succeed(None)
