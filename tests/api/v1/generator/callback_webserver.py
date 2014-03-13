#!/usr/bin/env python

from flask import Flask, request
import argparse
import requests
import signal


_REMAINING_CALLBACKS_EXPECTED = None
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--expected-callbacks', type=int, default=1)
    parser.add_argument('--port', type=int, default=5113)
    parser.add_argument('--stop-after', type=int, default=10)

    arguments = parser.parse_args()

    global _REMAINING_CALLBACKS_EXPECTED
    _REMAINING_CALLBACKS_EXPECTED = arguments.expected_callbacks

    return arguments


app = Flask(__name__)


@app.route('/<path:callback_name>', methods=['PUT'])
def log_request(callback_name):
    print callback_name

    decrement_callback_count()
    send_request()

    return ''


def decrement_callback_count():
    global _REMAINING_CALLBACKS_EXPECTED
    _REMAINING_CALLBACKS_EXPECTED -= 1
    if _REMAINING_CALLBACKS_EXPECTED <= 0:
        shutdown_server()


def send_request():
    if 'request_name' in request.args:
        url = request.json.get('callbacks').get(request.args['request_name'])
        data = dict(request.args)
        del data['request_name']
        requests.put(url, data)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


if __name__ == '__main__':
    arguments = parse_arguments()
    signal.alarm(arguments.stop_after)
    app.run(port=arguments.port)
