from ptero_petri.implementation import exit_codes
from ptero_petri.implementation.configuration.commands import determine_command
from ptero_petri.implementation.configuration.inject.initialize import initialize_injector
from ptero_petri.implementation.configuration.parser import parse_arguments
from ptero_petri.implementation.configuration.settings.load import load_settings
from ptero_petri.implementation.util import signal_handlers
import logging
import logging.config
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


def _get_logging_configuration():
    level = _get_logging_level()
    return {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': level,
            'handlers': ['console'],
        },

        'formatters': {
            'plain': {
                'format': '%(asctime)s %(levelname)s %(name)s %(funcName)s '
                            '%(lineno)d: %(message)s',
            },
        },

        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'plain',
            },
        },

        'loggers': {
            'ptero_petri': {
                'level': level,
            },
            'pika': {
                'level': 'INFO',
            },
        },
    }


def _get_logging_level():
    return os.environ.get('PTERO_PETRI_LOG_LEVEL', 'INFO').upper()


def naked_main():
    command_class = determine_command()
    parsed_args = parse_arguments(command_class)

    settings = load_settings(command_class.name, parsed_args)

    logging.config.dictConfig(_get_logging_configuration())

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
