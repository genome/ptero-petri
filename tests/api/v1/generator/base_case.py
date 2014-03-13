import abc
import collections
import jinja2
import os
import requests
import signal
import simplejson
import subprocess
import time
import urllib
import urlparse
import yaml


_POLLING_DELAY = 0.05
_TERMINATE_WAIT_TIME = 0.05

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


    def setUp(self):
        super(TestCaseMixin, self).setUp()
        self._clear_memoized_data()

        self._purge_rabbitmq()
        self._purge_redis()

        self._start_petri_worker()
        self._start_petri_api_webserver()
        self._start_callback_receipt_webserver()

    def tearDown(self):
        super(TestCaseMixin, self).tearDown()
        self._stop_callback_receipt_webserver()
        self._stop_petri_api_webserver()
        self._stop_petri_worker()


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
        done = False
        while not done:
            stuff = self._callback_webserver.poll()
            if stuff is not None:
                done = True
            if not done:
                time.sleep(_POLLING_DELAY)

    def _verify_expected_callbacks(self):
        self._verify_callback_order(self.expected_callbacks,
                self.actual_callbacks)
        self._verify_callback_counts(self.expected_callbacks,
                self.actual_callbacks)

    def _verify_callback_order(self, expected_callbacks, actual_callbacks):
        seen_callbacks = set()

        for callback in actual_callbacks:
            for prereq_callback in _get_prereq_callbacks(expected_callbacks,
                    callback):
                if prereq_callback not in seen_callbacks:
                    self.fail("Have not yet seen callback '%s' "
                            "depended on by callback '%s'."
                            "  Seen callbacks:  %s" % (
                                prereq_callback,
                                callback,
                                seen_callbacks
                    ))
            seen_callbacks.add(callback)

    def _verify_callback_counts(self, expected_callbacks, actual_callbacks):
        actual_callback_counts = _get_actual_callback_counts(actual_callbacks)
        expected_callback_counts = _get_expected_callback_counts(
                expected_callbacks)
        self.assertEqual(expected_callback_counts, actual_callback_counts)

    @property
    def actual_callbacks(self):
        if self._actual_callbacks is None:
            stdout, stderr = self._callback_webserver.communicate()
            self._actual_callbacks = stdout.splitlines()
        return self._actual_callbacks

    @property
    def _net_body(self):
        body = None
        with open(self._net_file_path) as f:
            template = jinja2.Template(f.read())
            body = template.render(callback_url=self._callback_url)
        return simplejson.loads(body)

    def _callback_url(self, callback_name, request_name=None, **request_data):
        if request_name is not None:
            request_data['request_name'] = request_name

        return '"%s"' % self._assemble_callback_url(callback_name, request_data)

    def _assemble_callback_url(self, callback_name, request_data):
        return urlparse.urlunparse((
            'http',
            'localhost:%d' % self.callback_port,
            '/' + callback_name,
            '',
            urllib.urlencode(request_data),
            '',
        ))

    @property
    def _net_file_path(self):
        return os.path.join(self.directory, 'net.json')

    @property
    def expected_callbacks(self):
        if not self._expected_callbacks:
            with open(self._expected_callbacks_path) as f:
                self._expected_callbacks = yaml.load(f)
        return self._expected_callbacks

    @property
    def _expected_callbacks_path(self):
        return os.path.join(self.directory, 'expected_callbacks.yaml')

    @property
    def _total_expected_callbacks(self):
        return sum(_get_expected_callback_counts(
            self.expected_callbacks).itervalues())


    def _clear_memoized_data(self):
        self._actual_callbacks = None
        self._expected_callbacks = None


    def _purge_rabbitmq(self):
        pass

    def _purge_redis(self):
        pass


    def _start_petri_worker(self):
        pass

    def _start_petri_api_webserver(self):
        pass

    def _start_callback_receipt_webserver(self):
        self._callback_webserver = subprocess.Popen(
                [self._callback_webserver_path,
                    '--expected-callbacks', str(self._total_expected_callbacks),
                    '--stop-after', str(self._max_wait_time),
                    ],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _stop_callback_receipt_webserver(self):
        try:
            self._callback_webserver.send_signal(signal.SIGINT)
            time.sleep(_TERMINATE_WAIT_TIME)
            self._callback_webserver.kill()
        except OSError as e:
            if e.errno != 3:  # errno 3: no such pid
                raise

    def _stop_petri_api_webserver(self):
        pass

    def _stop_petri_worker(self):
        pass

    @property
    def _callback_webserver_path(self):
        return os.path.join(os.path.dirname(__file__), 'callback_webserver.py')

    @property
    def _max_wait_time(self):
        return 10


def _get_prereq_callbacks(expected_callbacks, callback):
    expected_callback_data = expected_callbacks.get(callback, {})
    return expected_callback_data.get('depends', [])


def _get_actual_callback_counts(actual_callbacks):
    counts = collections.defaultdict(int)
    for cb in actual_callbacks:
        counts[cb] += 1
    return dict(counts)


def _get_expected_callback_counts(expected_callbacks):
    return {callback: data['count']
            for callback, data in expected_callbacks.iteritems()}
