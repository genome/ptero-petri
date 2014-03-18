from .. helpers.builder_test_base import BuilderTestBase
from .. helpers.redistest import RedisTest
from unittest import TestCase, main


class TestBuilderSystemTests(BuilderTestBase, RedisTest):
    def setUp(self):
        RedisTest.setUp(self)
        BuilderTestBase.setUp(self)


if __name__ == "__main__":
    main()
