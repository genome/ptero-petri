from injector import inject, Injector
from ptero_petri.implementation import exit_codes
from ptero_petri.implementation import interfaces
from ptero_petri.implementation.configuration.inject.broker import BrokerConfiguration
from ptero_petri.implementation.configuration.inject.redis_conf import RedisConfiguration
from ptero_petri.implementation.configuration.inject.service_locator import ServiceLocatorConfiguration
from ptero_petri.implementation.orchestrator.handlers import PetriCreateTokenHandler
from ptero_petri.implementation.orchestrator.handlers import PetriNotifyPlaceHandler
from ptero_petri.implementation.orchestrator.handlers import PetriNotifyTransitionHandler
from ptero_petri.implementation.util.exit import exit_process
from twisted.internet import defer
from twisted.internet import reactor
import logging
import traceback
import twisted.internet.error


LOG = logging.getLogger(__name__)


@inject(storage=interfaces.IStorage, broker=interfaces.IBroker,
        injector=Injector)
class OrchestratorCommand(object):
    name = 'orchestrator'

    injector_modules = [
            BrokerConfiguration,
            RedisConfiguration,
            ServiceLocatorConfiguration,
    ]

    def __init__(self, exit_code=0):
        self.exit_code = exit_code

    def _setup(self, *args, **kwargs):
        self.handlers = [
                self.injector.get(PetriCreateTokenHandler),
                self.injector.get(PetriNotifyPlaceHandler),
                self.injector.get(PetriNotifyTransitionHandler)
        ]

        for handler in self.handlers:
            self.broker.register_handler(handler)

        reactor.callWhenRunning(self._execute_and_stop)

    def _execute(self):
        """
        Returns a deferred that will never fire.
        """
        deferred = defer.Deferred()
        return deferred

    def _execute_and_stop(self):
        try:
            deferred = self._execute()
            d = deferred.addCallbacks(self._stop, self._exit)
            d.addErrback(self._exit)
            return deferred
        except:
            LOG.exception("Unexpected exception while executing command")
            exit_process(exit_codes.EXECUTE_FAILURE)

    def _stop(self, _callback):
        LOG.debug("Stopping the twisted reactor.")
        reactor.stop()
        return _callback

    def _exit(self, error):
        LOG.critical("Unexpected error while executing command\n%s", error.getTraceback())
        exit_process(exit_codes.EXECUTE_FAILURE)

    def _teardown(self):
        """
        Anything that should be done after the reactor has been
        stopped.
        """
        pass

    def execute(self):
        self._setup()
        try:
            reactor.run()
        except twisted.internet.error.ReactorNotRunning:
            print 'omg lol?'
            traceback.print_exc()
        finally:
            self._teardown()
        return self.exit_code


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
        exit_code = command.execute()
    except:
        LOG.exception('Command execution failed')
        return exit_codes.EXECUTE_FAILURE

    return exit_code


if __name__ == '__main__':
    main()
