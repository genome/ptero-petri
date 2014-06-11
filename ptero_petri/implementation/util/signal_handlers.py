from .. import exit_codes
from .exit import exit_process
import logging
import signal


LOG = logging.getLogger(__name__)


def setup_standard_signal_handlers():
    setup_exit_handler(signal.SIGTERM)


def setup_exit_handler(signum):
    def _handler(signum, frame):
        LOG.critical('Received signal %d: %s', signum, frame)
        exit_process(exit_codes.UNKNOWN_ERROR)
    signal.signal(signum, _handler)
