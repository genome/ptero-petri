import abc
import collections
import errno
import jinja2
import json
import os
import redis
import requests
import signal
import subprocess
import sys
import time
import urllib
import urlparse
import yaml


_POLLING_DELAY = 0.05
_TERMINATE_WAIT_TIME = 0.05

_MAX_RETRIES = 100
_RETRY_DELAY = 0.15


def validate_json(text):
    json.loads(text)


class TestCaseMixin(object):
    __metaclass__ = abc.ABCMeta

    @property
    def api_host(self):
        return os.environ['PTERO_PETRI_HOST']

    @property
    def api_port(self):
        return int(os.environ['PTERO_PETRI_PORT'])

    @abc.abstractproperty
    def directory(self):
        pass

    @abc.abstractproperty
    def test_name(self):
        pass

    @property
    def connection(self):
        return redis.Redis(host=os.environ['PTERO_PETRI_REDIS_HOST'],
                port=os.environ['PTERO_PETRI_REDIS_PORT'])

    def setUp(self):
        super(TestCaseMixin, self).setUp()
        self.connection.flushall()

    def tearDown(self):
        super(TestCaseMixin, self).tearDown()

    def _submit_net(self):
        response = _retry(requests.post, self._submit_url, self._net_body,
                          headers={'content-type': 'application/json'})
        self.assertEqual(201, response.status_code)

    @property
    def _submit_url(self):
        return 'http://%s:%d/v1/nets' % (self.api_host, self.api_port)

    @property
    def _net_body(self):
        body = None
        with open(self._net_file_path) as f:
            template = jinja2.Template(f.read())
            body = template.render(webhook_url=self._webhook_url)
            validate_json(body)
        return body

    @property
    def _net_file_path(self):
        return os.path.join(self.directory, 'net.json')


class TestWebhooksMixin(TestCaseMixin):
    @staticmethod
    def _get_prereq_webhooks(expected_webhooks, webhook):
        expected_webhook_data = expected_webhooks.get(webhook, {})
        return expected_webhook_data.get('depends', [])

    @staticmethod
    def _get_actual_webhook_counts(actual_webhooks):
        counts = collections.defaultdict(int)
        for cb in actual_webhooks:
            counts[cb] += 1
        return dict(counts)

    @staticmethod
    def _get_expected_webhook_counts(expected_webhooks):
        return {webhook: data['count']
                for webhook, data in expected_webhooks.iteritems()}

    @property
    def webhook_host(self):
        return os.environ['PTERO_PETRI_TEST_WEBHOOK_CALLBACK_HOST']

    @abc.abstractproperty
    def webhook_port(self):
        pass

    def setUp(self):
        super(TestWebhooksMixin, self).setUp()
        self._clear_memoized_data()

        self._start_webhook_receipt_webserver()

    def tearDown(self):
        super(TestWebhooksMixin, self).tearDown()
        self._stop_webhook_receipt_webserver()

    def _wait_for_webhook_output(self):
        done = False
        while not done:
            stuff = self._webhook_webserver.poll()
            if stuff is not None:
                done = True
                stdout, stderr = self._webhook_webserver.communicate()
                self._webhook_stdout = stdout
                self._webhook_stderr = stderr

            if not done:
                time.sleep(_POLLING_DELAY)

    def _print_webhook_server_output(self):
        self._write_with_banner('STDOUT', self._webhook_stdout)
        self._write_with_banner('STDERR', self._webhook_stderr)

    def _write_with_banner(self, label, data):
        sys.stdout.write('--- Begin webhook server %s ---\n' % label)
        sys.stdout.write(data)
        sys.stdout.write('--- End webhook server %s ---\n' % label)

    def _verify_expected_webhooks(self):
        self._verify_webhook_order(self.expected_webhooks, self.actual_webhooks)
        self._verify_webhook_counts(self.expected_webhooks,
                                    self.actual_webhooks)

    def _verify_webhook_order(self, expected_webhooks, actual_webhooks):
        seen_webhooks = set()

        for webhook in actual_webhooks:
            for prereq_webhook in self._get_prereq_webhooks(expected_webhooks,
                                                       webhook):
                if prereq_webhook not in seen_webhooks:
                    self.fail("Have not yet seen webhook '%s' "
                              "depended on by webhook '%s'."
                              "  Seen webhooks:  %s" % (
                                  prereq_webhook,
                                  webhook,
                                  seen_webhooks
                              ))
            seen_webhooks.add(webhook)

    def _verify_webhook_counts(self, expected_webhooks, actual_webhooks):
        actual_webhook_counts = self._get_actual_webhook_counts(actual_webhooks)
        expected_webhook_counts = self._get_expected_webhook_counts(
            expected_webhooks)
        self.assertEqual(expected_webhook_counts, actual_webhook_counts)

    @property
    def actual_webhooks(self):
        if self._actual_webhooks is None:
            self._actual_webhooks = self._webhook_stdout.splitlines()
        return self._actual_webhooks

    def _webhook_url(self, webhook_name, request_name=None, **request_data):
        if request_name is not None:
            request_data['request_name'] = request_name

        return '"%s"' % self._assemble_webhook_url(webhook_name, request_data)

    def _assemble_webhook_url(self, webhook_name, request_data):
        return urlparse.urlunparse((
            'http',
            '%s:%d' % (self.webhook_host, self.webhook_port),
            '/webhooks/' + webhook_name,
            '',
            urllib.urlencode(request_data),
            '',
        ))

    @property
    def expected_webhooks(self):
        if not self._expected_webhooks:
            with open(self._expected_webhooks_path) as f:
                self._expected_webhooks = yaml.load(f)
        return self._expected_webhooks

    @property
    def _expected_webhooks_path(self):
        return os.path.join(self.directory, 'expected_webhooks.yaml')

    @property
    def _total_expected_webhooks(self):
        return sum(self._get_expected_webhook_counts(
            self.expected_webhooks).itervalues())

    def _clear_memoized_data(self):
        self._actual_webhooks = None
        self._expected_webhooks = None

    def _start_webhook_receipt_webserver(self):
        self._webhook_webserver = subprocess.Popen(
            [self._webhook_webserver_path,
             '--expected-webhooks', str(
                 self._total_expected_webhooks),
             '--stop-after', str(self._max_wait_time),
             '--port', str(self.webhook_port),
             ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._wait_for_webhook_webserver()

    def _wait_for_webhook_webserver(self):
        response = _retry(requests.get, self._webhook_ping_url())
        if response.status_code != 200:
            raise RuntimeError('Failed to spin up webhook webserver: %s'
                               % response.text)

    def _webhook_ping_url(self):
        return 'http://%s:%d/ping' % (
            self.webhook_host, self.webhook_port)

    def _stop_webhook_receipt_webserver(self):
        _stop_subprocess(self._webhook_webserver)

    @property
    def _webhook_webserver_path(self):
        return os.path.join(os.path.dirname(__file__), 'webhook_webserver.py')

    @property
    def _max_wait_time(self):
        return 20

    def test_got_expected_webhooks(self):
        self._submit_net()

        self._wait_for_webhook_output()
        self._print_webhook_server_output()

        self._verify_expected_webhooks()


def _stop_subprocess(process):
    try:
        process.send_signal(signal.SIGINT)
        time.sleep(_TERMINATE_WAIT_TIME)
        process.kill()
        time.sleep(_TERMINATE_WAIT_TIME)
    except OSError as e:
        if e.errno != errno.ESRCH:  # ESRCH: no such pid
            raise


def _retry(func, *args, **kwargs):
    for attempt in xrange(_MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except:
            time.sleep(_RETRY_DELAY)
    error_msg = "Failed (%s) with args (%s) and kwargs (%s) %d times" % (
        func.__name__, args, kwargs, _MAX_RETRIES)
    raise RuntimeError(error_msg)
