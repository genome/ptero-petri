from ...container_utils import head
from .base import BasicActionBase
from twisted.internet import defer


class SplitAction(BasicActionBase):
    def execute(self, net, color_descriptor, active_tokens, service_interfaces):
        input_token = net.token(head(active_tokens))

        color_group_idx = int(input_token.data['color_group_idx'])
        color_group = net.color_group(color_group_idx)

        tokens = self._create_tokens(color_group, net=net)

        return tokens, defer.succeed(None)

    def _create_tokens(self, color_group, net):
        tokens = []
        for color in color_group.color_iter:
            tokens.append(net.create_token(color=color,
                color_group_idx=color_group.idx))

        return tokens
