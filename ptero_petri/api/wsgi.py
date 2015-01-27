from ptero_petri.api import application
from ptero_common.logging_configuration import configure_web_logging
import argparse

app = application.create_app()

configure_web_logging("PETRI")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--debug', action='store_true', default=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    app.run(port=args.port, debug=args.debug)
