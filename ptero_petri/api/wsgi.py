from ptero_petri.api import application
from ptero_common.logging_configuration import configure_web_logging
import os

app = application.create_app()
configure_web_logging("PETRI")


def handle_sigterm(signum, frame):
    import sys
    sys.stderr.write('Handling SIGTERM... shutting down the Flask Server')
    shutdown_server()


def shutdown_server():
    raise RuntimeError('Forcefully shutting down the Flask Server')


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGTERM, handle_sigterm)

    app.run(
        host='0.0.0.0',
        port=os.environ['PTERO_PETRI_PORT'],
        debug=False, use_reloader=False)
