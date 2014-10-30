from .. import exceptions
from .. import lua
from ... import rom
from ...container_utils import head
from .base import BarrierActionBase, BasicActionBase


_merge_hashes_script = rom.Script(lua.load('merge_hashes'))


class MergeMixin(object):
    def merge_data(self, net, dest_token, active_tokens):
        keys = [dest_token.data.key]
        keys.extend(net.token(t).data.key for t in active_tokens)
        rv = _merge_hashes_script(connection=self.connection, keys=keys)
        if rv[0] != 0:
            raise exceptions.BadTokenDataError(
                    'Failed to merge token data for tokens: %s'
                    % [t for t in active_tokens])

    def get_merged_token(self, net, color, color_group_idx, active_tokens):
        if len(active_tokens) == 1:
            new_token_idx = head(active_tokens)
            new_token = net.token(new_token_idx)

        else:
            new_token = net.create_token(color=color,
                    color_group_idx=color_group_idx)
            self.merge_data(net, new_token, active_tokens)

        return new_token


class BasicMergeAction(BasicActionBase, MergeMixin):
    def execute(self, net, color_descriptor, active_tokens):
        new_token = self.get_merged_token(net, color=color_descriptor.color,
                color_group_idx=color_descriptor.group.idx,
                active_tokens=active_tokens)

        return [new_token]


class BarrierMergeAction(BarrierActionBase, MergeMixin):
    def execute(self, net, color_descriptor, active_tokens):
        raise NotImplementedError(":(")
