import os
from os import environ
import jinja2

BASE_PATH = os.path.dirname(__file__)


def get_template_data():
    result = {}
    for filename in os.listdir(BASE_PATH):
        module, extension = os.path.splitext(filename)
        if extension.endswith('template'):
            fullpath = os.path.join(BASE_PATH, filename)
            template = jinja2.Template(open(fullpath).read())
            result[module] = template.render(environment=environ)
    result['environment'] = environ
    return result


TEMPLATE_DATA = get_template_data()


def load(module_name, template_data=TEMPLATE_DATA):
    filename = os.path.join(BASE_PATH, '%s.lua' % module_name)

    with open(filename) as f:
        template = jinja2.Template(f.read())
    return template.render(**template_data)
