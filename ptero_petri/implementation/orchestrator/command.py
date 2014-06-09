from ptero_petri.implementation.configuration.inject.broker import BrokerConfiguration
from ptero_petri.implementation.configuration.inject.redis_conf import RedisConfiguration
from ptero_petri.implementation.configuration.inject.service_locator import ServiceLocatorConfiguration
from ptero_petri.implementation.orchestrator.handlers import PetriCreateTokenHandler
from ptero_petri.implementation.orchestrator.handlers import PetriNotifyPlaceHandler
from ptero_petri.implementation.orchestrator.handlers import PetriNotifyTransitionHandler
from ptero_petri.implementation.orchestrator.service_command import ServiceCommand
import logging


LOG = logging.getLogger(__name__)


class OrchestratorCommand(ServiceCommand):
    name = 'orchestrator'

    injector_modules = [
            BrokerConfiguration,
            RedisConfiguration,
            ServiceLocatorConfiguration,
    ]

    def _setup(self, *args, **kwargs):
        self.handlers = [
                self.injector.get(PetriCreateTokenHandler),
                self.injector.get(PetriNotifyPlaceHandler),
                self.injector.get(PetriNotifyTransitionHandler)
        ]

        return ServiceCommand._setup(self, *args, **kwargs)


from ptero_petri.implementation import exit_codes
from ptero_petri.implementation.configuration.inject.initialize import initialize_injector
from ptero_petri.implementation.configuration.parser import parse_arguments
from ptero_petri.implementation.util import signal_handlers
import os
import pika
import sys
import traceback


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
    parsed_args = parse_arguments(command_class)

    injector = initialize_injector(command_class)

    # XXX Hack to get the command to show up in the rabbitmq admin interface
    pika.connection.PRODUCT = command_class.name

    try:
        LOG.info('Loading command (%s)', command_class.name)
        command = injector.get(command_class)
    except:
        LOG.exception('Could not instantiate command object.')
        return exit_codes.EXECUTE_ERROR

    try:
        exit_code = command.execute(parsed_args)
    except:
        LOG.exception('Command execution failed')
        return exit_codes.EXECUTE_FAILURE

    return exit_code


if __name__ == '__main__':
    main()
