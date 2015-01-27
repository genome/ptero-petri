from ptero_petri.api import application
from ptero_common.logging_configuration import configure_logging
import argparse
import logging
import os

app = application.create_app()

configure_logging('PTERO_PETRI_LOG_LEVEL', 'PTERO_PETRI_LOG_WITH_TIMESTAMPS')
logging.getLogger('pika').setLevel(
    os.environ.get('PTERO_PETRI_PIKA_LOG_LEVEL', 'WARN'))
logging.getLogger('requests').setLevel(
    os.environ.get('PTERO_PETRI_REQUESTS_LOG_LEVEL', 'WARN'))
logging.getLogger('werkzeug').setLevel(
    os.environ.get('PTERO_PETRI_WERKZEUG_LOG_LEVEL', 'WARN'))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--debug', action='store_true', default=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    app.run(port=args.port, debug=args.debug)
