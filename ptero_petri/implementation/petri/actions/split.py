from ...container_utils import head
from .base import BasicActionBase
from twisted.internet import defer


class SplitAction(BasicActionBase):
    def execute(self, net, color_descriptor, active_tokens, service_interfaces):
        input_token = net.token(head(active_tokens))

        num_tokens = int(input_token.data['split_size'])

        tokens = self._create_tokens(num_tokens=num_tokens,
                color_descriptor=color_descriptor, net=net)

        return tokens, defer.succeed(None)

    def _create_tokens(self, num_tokens, color_descriptor, net):
        new_color_group = net.add_color_group(size=num_tokens,
                parent_color=color_descriptor.color,
                parent_color_group_idx=color_descriptor.group.idx)

        tokens = []
        for i in xrange(num_tokens):
            color = new_color_group.begin + i

            tokens.append(net.create_token(color=color,
                color_group_idx=new_color_group.idx))

        return tokens
