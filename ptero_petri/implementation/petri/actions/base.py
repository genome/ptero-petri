from ... import rom


class ActionBase(rom.Object):
    required_arguments = []

    args = rom.Property(rom.Hash, value_encoder=rom.json_enc,
            value_decoder=rom.json_dec)
    response_places = rom.Property(rom.Hash, value_encoder=int,
            value_decoder=int)

    @property
    def name(self):
        return '%s (%s)' % (self.__class__, self.key)

    def _on_create(self):
        for argname in self.required_arguments:
            if not argname in self.args:
                raise TypeError("In class %s: required argument %s missing" %
                        (self.__class__.__name__, argname))


    def execute(self, net, color_descriptor, active_tokens):
        raise NotImplementedError("In class %s: execute not implemented"
                % self.__class__.__name__)


class BarrierActionBase(ActionBase):
    pass


class BasicActionBase(ActionBase):
    def get_merged_token_data(self, net, active_tokens):
        result = {}
        tokens = [net.token(t) for t in active_tokens]
        for t in tokens:
            result.update(t.data.value)
        return result
