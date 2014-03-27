from ptero_petri.implementation import exit_codes
from ptero_petri.implementation.configuration import defaults
from ptero_petri.implementation.configuration.commands import determine_command
from ptero_petri.implementation.configuration.inject.initialize import initialize_injector
from ptero_petri.implementation.configuration.parser import parse_arguments
from ptero_petri.implementation.configuration.settings.load import load_settings
from ptero_petri.implementation.util import signal_handlers
from ptero_petri.implementation.util.exit import exit_process
import logging.config
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



def naked_main():
    command_class = determine_command()
    parsed_args = parse_arguments(command_class)

    settings = load_settings(command_class.name, parsed_args)

    logging.config.dictConfig(settings.get('logging',
        defaults.DEFAULT_LOGGING_CONFIG))

    injector = initialize_injector(settings, command_class)


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
