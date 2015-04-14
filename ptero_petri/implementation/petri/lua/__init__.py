import os.path

BASE_PATH = os.path.dirname(__file__)


def load(module_name):
    filename = os.path.join(BASE_PATH, '%s.lua' % module_name)
    return open(filename).read()
