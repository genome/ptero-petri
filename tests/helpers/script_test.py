from ptero_petri.implementation import lua
from .. helpers.redistest import RedisTest

import ptero_petri.redisom as rom
import unittest


def create_holder_class(script_name):
    class Holder(rom.Object):
        script = rom.Script(lua.load(script_name))

    return Holder

class ScriptTest(object):
    def setUp(self):
        RedisTest.setUp(self)

        cls = create_holder_class(self.SCRIPT_NAME)
        self.h = cls(self.conn, key='h')
        self.script = self.h.script
