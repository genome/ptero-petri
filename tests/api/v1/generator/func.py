from .base_case import TestCaseMixin
import os
import unittest


def create_test_cases(target_module, test_case_directory):
    for test_case_name in os.listdir(test_case_directory):
        _create_and_attach_test_case(target_module, test_case_directory,
                test_case_name)


def _create_and_attach_test_case(target_module, test_case_directory,
        test_case_name):
    tc = _create_test_case(test_case_directory, test_case_name)
    _attach_test_case(target_module, tc)


def _create_test_case(test_case_directory, test_case_name):
    class_dict = {
        'directory': os.path.join(test_case_directory, test_case_name),
        'port': 8822,
    }
    return type(test_case_name, (TestCaseMixin, unittest.TestCase),
            class_dict)


def _attach_test_case(target_module, test_case):
    setattr(target_module, test_case.__class__.__name__, test_case)
