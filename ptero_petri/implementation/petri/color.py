from .. import rom
from collections import namedtuple


Color = int


_ColorGroupBase = namedtuple("_ColorGroupBase", ["idx", "parent_color",
        "parent_color_group_idx", "begin", "end"])

class ColorGroup(_ColorGroupBase):
    @property
    def size(self):
        return self.end - self.begin

    @property
    def colors(self):
        return range(self.begin, self.end)

    @property
    def color_iter(self):
        return xrange(self.begin, self.end)

    @property
    def as_dict(self):
        return dict(self._asdict())



def color_group_enc(value):
    return rom.json_enc(value._asdict())


def color_group_dec(value):
    return ColorGroup(**rom.json_dec(value))


_ColorDescriptorBase = namedtuple("_ColorDescriptorBase", ["color", "group"])

class ColorDescriptor(_ColorDescriptorBase):
    @property
    def as_dict(self):
        return dict(self._asdict())
