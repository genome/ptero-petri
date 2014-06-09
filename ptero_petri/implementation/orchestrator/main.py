from ptero_petri.implementation import exit_codes
from ptero_petri.implementation.configuration.inject.initialize import initialize_injector
from ptero_petri.implementation.orchestrator.command import OrchestratorCommand
from ptero_petri.implementation.util import signal_handlers
from twisted.internet import reactor
import logging
import os
import pika
import sys
import traceback


LOG = logging.getLogger(__name__)


def main():
    try:
        signal_handlers.setup_standard_signal_handlers()

        exit_code = naked_main()

    except SystemExit as e:
        exit_code = e.code
    except:
        sys.stderr.write('Unhandled exception:\n')
        traceback.print_exc()
        exit_code = exit_codes.UNKNOWN_ERROR

    return exit_code


def _get_logging_level():
    return os.environ.get('PTERO_PETRI_LOG_LEVEL', 'INFO').upper()


def naked_main():
    logging.basicConfig(level=_get_logging_level())

    command_class = OrchestratorCommand

    injector = initialize_injector()

    # XXX Hack to get the command to show up in the rabbitmq admin interface
    pika.connection.PRODUCT = command_class.name

    try:
        LOG.info('Loading command (%s)', command_class.name)
        command = injector.get(command_class)
    except:
        LOG.exception('Could not instantiate command object.')
        return exit_codes.EXECUTE_ERROR

    reactor.run()

    LOG.info('Orchestrator exiting...')
    return exit_codes.EXECUTE_FAILURE


if __name__ == '__main__':
    main()
