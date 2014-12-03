from .base import BarrierActionBase


class JoinAction(BarrierActionBase):

    def execute(self, net, color_descriptor, active_tokens):
        parent_group_idx = color_descriptor.group.parent_color_group_idx
        token = net.create_token(color=color_descriptor.group.parent_color,
                                 color_group_idx=parent_group_idx)

        return [token]
