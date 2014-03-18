from ptero_petri.implementation import lua

from unittest import TestCase, main

import mock
import os.path


class TestLoadLua(TestCase):
    def setUp(self):
        self.base_path = os.path.join(os.path.dirname(__file__), 'data')

    def test_single_file(self):
        with mock.patch('ptero_petri.implementation.lua.BASE_PATH', self.base_path):
            script = lua.load('alpha')
        self.assertEqual(script, 'AAA\n')

    def test_multiple_files(self):
        with mock.patch('ptero_petri.implementation.lua.BASE_PATH', self.base_path):
            script = lua.load('alpha', 'bravo')
        self.assertEqual(script, 'AAA\n\nBBB\n')


if __name__ == "__main__":
    main()
