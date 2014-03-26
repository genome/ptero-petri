from .. import exceptions
from .. import lua
from ... import rom
from ...container_utils import head
from .base import BarrierActionBase, BasicActionBase
from twisted.internet import defer


class MergeMixin(object):
    def merge_data(self, net, dest_token, active_tokens):
        keys = [dest_token.data.key]
        keys.extend(net.token(t).data.key for t in active_tokens)
        rv = self._merge_hashes_script(keys=keys)
        if rv[0] != 0:
            raise exceptions.BadTokenDataError(
                    'Failed to merge token data for tokens: %s'
                    % [t for t in active_tokens])



class BasicMergeAction(BasicActionBase, MergeMixin):
    _merge_hashes_script = rom.Script(lua.load('merge_hashes'))

    def execute(self, net, color_descriptor,
            active_tokens, service_interfaces):
        if len(active_tokens) == 1:
            new_token_idx = head(active_tokens)
            new_token = net.token(new_token_idx)
        else:
            new_token = net.create_token(color=color_descriptor.color,
                    color_group_idx=color_descriptor.group.idx)
            self.merge_data(net, new_token, active_tokens)

        return [new_token], defer.succeed(None)


class BarrierMergeAction(BarrierActionBase, MergeMixin):
    _merge_hashes_script = rom.Script(lua.load('merge_hashes'))

    def execute(self, net, color_descriptor,
            active_tokens, service_interfaces):
        raise NotImplementedError(":(")
