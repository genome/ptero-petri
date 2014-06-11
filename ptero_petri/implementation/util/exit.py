import logging
import os


LOG = logging.getLogger(__name__)


def exit_process(exit_code):
    LOG.info('Exitting process.')

    os._exit(exit_code)
