from ..redishelpers import redistest
from .helpers import script_test


class TestBuilderSystemTests(redistest.RedisTest, script_test.ScriptTest):

    def setUp(self):
        redistest.RedisTest.setUp(self)
        script_test.ScriptTest.setUp(self)
