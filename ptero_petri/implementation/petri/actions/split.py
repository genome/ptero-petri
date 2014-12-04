from .base import BasicActionBase


class SplitAction(BasicActionBase):

    def execute(self, net, color_descriptor, active_tokens):
        merged_data = self.get_merged_token_data(net, active_tokens)

        color_group_idx = int(merged_data['color_group_idx'])
        color_group = net.color_group(color_group_idx)

        tokens = self._create_tokens(color_group, net=net)

        return tokens

    def _create_tokens(self, color_group, net):
        tokens = []
        for color in color_group.color_iter:
            tokens.append(net.create_token(color=color,
                                           color_group_idx=color_group.idx))

        return tokens
