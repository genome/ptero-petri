from .redistest import RedisTest
from ptero_petri.implementation import rom
from ptero_petri.implementation.petri import lua
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
