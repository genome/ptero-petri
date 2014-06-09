from injector import inject
from ptero_petri.implementation import exit_codes
from ptero_petri.implementation import interfaces
from ptero_petri.implementation.orchestrator.handlers import PetriCreateTokenHandler
from ptero_petri.implementation.orchestrator.handlers import PetriNotifyPlaceHandler
from ptero_petri.implementation.orchestrator.handlers import PetriNotifyTransitionHandler
from ptero_petri.implementation.util.exit import exit_process
from twisted.internet import defer
from twisted.internet import reactor
import logging
import traceback


LOG = logging.getLogger(__name__)


@inject(storage=interfaces.IStorage, broker=interfaces.IBroker,
        create_token_handler=PetriCreateTokenHandler,
        notify_place_handler=PetriNotifyPlaceHandler,
        notify_transition_handler=PetriNotifyTransitionHandler)
class OrchestratorCommand(object):
    name = 'orchestrator'

    def __init__(self):
        self.broker.register_handler(self.create_token_handler)
        self.broker.register_handler(self.notify_place_handler)
        self.broker.register_handler(self.notify_transition_handler)

    def execute(self):
        reactor.run()


from ptero_petri.implementation.configuration.inject.initialize import initialize_injector
from ptero_petri.implementation.util import signal_handlers
import os
import pika
import sys


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

    try:
        command.execute()
    except:
        LOG.exception('Command execution failed')
        return exit_codes.EXECUTE_FAILURE

    LOG.error('This code should never be reached.')
    return exit_codes.EXECUTE_ERROR


if __name__ == '__main__':
    main()
