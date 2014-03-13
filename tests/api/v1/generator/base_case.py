import abc
import collections
import jinja2
import os
import requests
import simplejson
import yaml


class TestCaseMixin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def api_port(self):
        pass

    @abc.abstractproperty
    def callback_port(self):
        pass

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
        return 'http://localhost:%d/v1/nets' % self.api_port


    def _create_start_token(self, net_key):
        response = requests.post(self._start_place_url(net_key))
        self.assertEqual(201, response.status_code)

    def _start_place_url(self, net_key):
        return 'http://localhost:%d/v1/nets/%s/places/start/tokens' % (
                self.api_port, net_key)

    def _wait(self):
        pass

    def _verify_expected_callbacks(self):
        expected_callbacks = self._expected_callbacks
        seen_callback_counts = collections.defaultdict(int)

        for callback in self._actual_callbacks:
            for prereq_callback in _get_prereq_callbacks(expected_callback,
                    callback):
                if prereq_callback not in seen_callback_counts:
                    self.fail("Have not yet seen callback '%s' "
                            "depended on by callback '%s'."
                            "  Seen callbacks:  %s" % (
                                prereq_callback,
                                callback,
                                dict(seen_callback_counts)
                    ))
            seen_callback_counts[callback] += 1

        expected_callback_counts = _get_expected_callback_counts(
                expected_callbacks)
        self.assertEqual(expected_callback_counts, dict(seen_callback_counts))

    @property
    def _actual_callbacks(self):
        return []

    @property
    def _net_body(self):
        body = None
        with open(self._net_file_path) as f:
            template = jinja2.Template(f.read())
            body = template.render(callback_port=self.callback_port)
        return simplejson.loads(body)

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


def _get_prereq_callbacks(expected_callbacks, callback):
    expected_callback_data = expected_callbacks.get(callback, {})
    return expected_callback_data.get('depends', [])


def _get_expected_callback_counts(expected_callbacks):
    return {callback: data['count']
            for callback, data in expected_callbacks.iteritems()}
