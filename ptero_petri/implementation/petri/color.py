from .. import rom
from collections import namedtuple


Color = int


class ColorGroup(object):
    def __init__(self, idx, parent_color_group_idx, begin, end,
            color_lineage=None, parent_color=None):
        # NOTE: parent color is ignored

        self.idx = idx
        self.parent_color_group_idx = parent_color_group_idx
        self.begin = begin
        self.end = end

        if color_lineage:
            self.color_lineage = color_lineage

        else:
            self.color_lineage = []

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
    def parent_color(self):
        if not self.color_lineage:
            return
        return self.color_lineage[-1]

    @property
    def as_dict(self):
        return {
            "idx": self.idx,
            "begin": self.begin,
            "end": self.end,
            "parent_color": self.parent_color,  # XXX For legacy compat only
            "parent_color_group_idx": self.parent_color_group_idx,
            "color_lineage": self.color_lineage,
        }



def color_group_enc(value):
    return rom.json_enc(value.as_dict)


def color_group_dec(value):
    return ColorGroup(**rom.json_dec(value))


_ColorDescriptorBase = namedtuple("_ColorDescriptorBase", ["color", "group"])

class ColorDescriptor(_ColorDescriptorBase):
    @property
    def as_dict(self):
        return {
            "color": self.color,
            "group": self.group.as_dict,
        }
