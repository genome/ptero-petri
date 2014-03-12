import abc
import os
import requests
import simplejson
import yaml


class TestCaseMixin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def directory(self):
        pass


    def test_got_expected_callbacks(self):
        net_key = self._submit_net()
        self._create_start_token(net_key)
        self._wait()
        self._verify_expected_callbacks()


    def _submit_net(self):
        response = requests.post(self._submit_url, self._net_body)
        self.assertEqual(201, response.status_code)
        return response.json()['net_key']

    @property
    def _submit_url(self):
        return 'http://localhost:%d/v1/nets' % self.port


    def _create_start_token(self, net_key):
        response = requests.post(self._start_place_url(net_key))
        self.assertEqual(201, response.status_code)

    def _start_place_url(self, net_key):
        return 'http://localhost:%d/v1/nets/%s/places/start/tokens' % (
                self.port, net_key)

    def _wait(self):
        pass

    def _verify_expected_callbacks(self):
        expected_callbacks = self._expected_callbacks
        seen_callbacks = set()
        for callback in self._actual_callbacks:
            for prereq_callback in expected_callbacks[callback]:
                self.assertIn(prereq_callback, seen_callbacks)
            seen_callbacks.add(callback)

        self.assertEqual(set(expected_callbacks.iterkeys()), seen_callbacks)

    @property
    def _actual_callbacks(self):
        return []

    @property
    def _net_body(self):
        with open(self._net_file_path) as f:
            return simplejson.load(f)

    @property
    def _net_file_path(self):
        return os.path.join(self.directory, 'net.json')

    @property
    def _expected_callbacks(self):
        with open(self._expected_callbacks_path) as f:
            return yaml.load(f)

    @property
    def _expected_callbacks_path(self):
        return os.path.join(self.directory, 'expected_callbacks.yaml')
