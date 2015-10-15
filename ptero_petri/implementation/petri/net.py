from . import lua
from .. import rom
from .petri_tasks import execute_task
from .color import ColorGroup
from .color import color_group_enc, color_group_dec
from .exceptions import ForeignTokenError, PlaceNotFoundError
from .place import Place
from .token import Token
from uuid import uuid4

import base64
import itertools
from ptero_common import nicer_logging


LOG = nicer_logging.getLogger(__name__)


_TOKEN_KEY = "t"
_PLACE_KEY = "P"
_TRANSITION_KEY = "T"
_COLOR_KEY = "C"
_COLOR_GROUP_KEY = "G"


class Net(rom.Object):
    name = rom.Property(rom.String)
    color_groups = rom.Property(rom.Hash, value_encoder=color_group_enc,
                                value_decoder=color_group_dec)

    color_marking = rom.Property(
        rom.Hash, value_encoder=int, value_decoder=int)
    group_marking = rom.Property(
        rom.Hash, value_encoder=int, value_decoder=int)

    counters = rom.Property(rom.Hash, value_encoder=int, value_decoder=int)

    variables = rom.Property(rom.Hash, value_encoder=rom.json_enc,
                             value_decoder=rom.json_dec)
    _constants = rom.Property(rom.Hash, value_encoder=rom.json_enc,
                              value_decoder=rom.json_dec)

    _put_token_script = rom.Script(lua.load('put_token'))

    place_lookup = rom.Property(rom.Hash, value_encoder=int,
                                value_decoder=int)

    def additional_associated_iterkeys(self):
        return itertools.chain(*map(self.associated_iterkeys_for_attribute,
                                    ['place', 'token', 'transition']))

    def associated_iterkeys_for_attribute(self, attribute):
        for place_idx in xrange(getattr(self, 'num_%ss' % attribute)):
            obj = getattr(self, attribute)(place_idx)
            for key in obj.associated_iterkeys():
                yield key
            yield obj.key

    @classmethod
    def make_default_key(cls):
        return base64.urlsafe_b64encode(uuid4().bytes)[:-2]

    @property
    def num_places(self):
        return self.counters.get(_PLACE_KEY, 0)

    @num_places.setter
    def num_places(self, new_value):
        if self.counters.setnx(_PLACE_KEY, new_value) == 0:
            raise ValueError('Tried to overwrite num_places')

    @property
    def num_tokens(self):
        return self.counters.get(_TOKEN_KEY, 0)

    @property
    def num_transitions(self):
        return self.counters.get(_TRANSITION_KEY, 0)

    @num_transitions.setter
    def num_transitions(self, new_value):
        if self.counters.setnx(_TRANSITION_KEY, new_value) == 0:
            raise ValueError('Tried to overwrite num_transitions')

    def constant(self, key, default=None):
        return self._constants.get(key, default)

    def set_constant(self, key, value):
        if self._constants.setnx(key, value) == 0:
            raise TypeError("Tried to overwrite constant %s in net %s" %
                            (key, self.key))

    def set_variable(self, key, value):
        self.variables[key] = value

    def variable(self, key, default=None):
        return self.variables.get(key, default)

    def add_place(self, name):
        idx = self._incr_counter(_PLACE_KEY) - 1
        return Place.create(self.connection, self.place_key(idx),
                            index=idx, name=name)

    def add_transition(self, cls, *args, **kwargs):
        idx = self._incr_counter(_TRANSITION_KEY) - 1
        return cls.create(self.connection, self.transition_key(idx),
                          *args, **kwargs)

    def put_token(self, place_idx, token):
        if place_idx >= self.num_places:
            raise PlaceNotFoundError("Attempted to put token into place %s "
                                     "(%d places exist)" % (
                                         place_idx, self.num_places))

        token_idx = token.index.value
        if token.key != self.token_key(token_idx):
            raise ForeignTokenError("Token %s cannot be placed in net %s" %
                                    (token.key, self.key))

        keys = [self.color_marking.key, self.group_marking.key]
        args = [place_idx, token_idx, token.color.value,
                token.color_group_idx.value]

        rv = self._put_token_script(keys=keys, args=args)
        return rv

    def notify_place(self, place_idx, color):
        key = self.marking_key(color, place_idx)
        token_idx = self.color_marking.get(key)
        if token_idx is not None:
            place = self.place(place_idx)
            place.first_token_timestamp.setnx()

            arcs = place.arcs_out.value
            for transition_idx in arcs:
                execute_task('NotifyTransition', net_key=self.key,
                             transition_idx=transition_idx, place_idx=place_idx,
                             token_idx=token_idx)

    def notify_transition(self, transition_idx, place_idx, token_idx):
        trans = self.transition(transition_idx)
        token = self.token(token_idx)
        color_descriptor = token.color_descriptor

        consume_rv = trans.consume_tokens(place_idx, color_descriptor,
                                          self.color_marking.key,
                                          self.group_marking.key)

        if consume_rv == 0:
            new_tokens = trans.fire(self, color_descriptor)
            if not new_tokens:
                LOG.debug('Got no tokens from transition ("%s": %s) '
                          'on net (%s).', trans.name.value, trans.index,
                          self.key)
            colors = [x.color.value for x in new_tokens]
            trans.push_tokens(self, color_descriptor, new_tokens)
            trans.notify_places(self.key, colors)

    def color_group(self, idx):
        return self.color_groups[idx]

    def set_initial_color(self, initial_color):
        if self.counters.setnx(_COLOR_KEY, initial_color) == 0:
            raise ValueError("Cannot set initial color, since "
                             "color has already been incremented")

    def add_color_group(self, size, parent_color=None,
                        parent_color_group_idx=None):
        group_id = self._incr_counter(_COLOR_GROUP_KEY) - 1
        end = self._incr_counter(_COLOR_KEY, size)
        begin = end - size

        color_lineage = None
        begin_lineage = None
        if parent_color is not None and parent_color_group_idx is not None:
            parent_cg = self.color_groups[parent_color_group_idx]
            color_lineage = list(parent_cg.color_lineage)
            color_lineage.append(parent_color)
            begin_lineage = list(parent_cg.begin_lineage)
            begin_lineage.append(parent_cg.begin)

        cg = ColorGroup(idx=group_id,
                        parent_color_group_idx=parent_color_group_idx,
                        begin=begin, end=end,
                        color_lineage=color_lineage,
                        begin_lineage=begin_lineage)

        self.color_groups[group_id] = cg

        return cg

    def _incr_counter(self, which, size=1):
        return self.counters.incrby(which, size)

    def place_key(self, idx):
        return self.subkey(_PLACE_KEY, idx)

    def place(self, idx):
        return Place(self.connection, self.place_key(idx))

    def transition_key(self, idx):
        return self.subkey(_TRANSITION_KEY, idx)

    def transition(self, idx):
        return rom.get_object(self.connection, self.transition_key(idx))

    def token_key(self, idx):
        return self.subkey(_TOKEN_KEY, idx)

    def token(self, idx):
        return Token(self.connection, self.token_key(idx))

    def create_token(self, color, color_group_idx, data=None):
        idx = self._incr_counter(_TOKEN_KEY) - 1
        key = self.token_key(idx)
        return Token.create(self.connection, key, net_key=self.key,
                            index=idx, data=data, color=color,
                            color_group_idx=color_group_idx)

    def create_put_notify(self, place_idx, color, color_group_idx, data=None):
        token = self.create_token(color, color_group_idx, data)
        self.put_token(place_idx, token)
        self.notify_place(place_idx, color)

    @staticmethod
    def marking_key(tag, place_idx):
        return "%s:%s" % (tag, place_idx)

    def describe_color_marking(self):
        result = {}
        for key, token_idx in self.color_marking.value.iteritems():
            place_idx = key.split(':')[1]
            result[key] = (self.place(place_idx).name.value, token_idx)

        return result
