from .helpers import redistest, script_test
from unittest import TestCase, main


class TestBuilderSystemTests(redistest.RedisTest, script_test.ScriptTest):
    def setUp(self):
        redistest.RedisTest.setUp(self)
        script_test.ScriptTest.setUp(self)


if __name__ == "__main__":
    main()
