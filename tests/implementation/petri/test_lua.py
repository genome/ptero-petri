from ptero_petri.implementation.petri import lua
import mock
import os.path
import unittest


class TestLoadLua(unittest.TestCase):

    def setUp(self):
        self.base_path = os.path.join(os.path.dirname(__file__), 'data')

    def test_single_file(self):
        with mock.patch('ptero_petri.implementation.petri.lua.BASE_PATH',
                        self.base_path):
            script = lua.load('alpha')
        self.assertEqual(script, 'AAA')

    def test_file_with_template(self):
        with mock.patch('ptero_petri.implementation.petri.lua.BASE_PATH',
                        self.base_path):
            script = lua.load('example_with_template',
                    template_data={'example': 'B'})
        self.assertEqual(script, 'A\nB\nC')

    def test_get_template_data(self):
        os.environ['EXAMPLE_ENVIRONMENT_VARIABLE'] = 'ABC'
        with mock.patch('ptero_petri.implementation.petri.lua.BASE_PATH',
                        self.base_path):
            with mock.patch('ptero_petri.implementation.petri.lua.environ',
                    os.environ):
                data = lua.get_template_data()
        self.assertEqual(data.get('environment'), os.environ)
        self.assertEqual(data.get('example'), 'ABC')


if __name__ == "__main__":
    unittest.main()
