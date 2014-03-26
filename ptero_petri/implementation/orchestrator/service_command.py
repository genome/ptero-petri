from .. import interfaces
from ..command_base import CommandBase
from injector import inject, Injector
from twisted.internet import defer
import logging


LOG = logging.getLogger(__name__)


@inject(storage=interfaces.IStorage, broker=interfaces.IBroker,
        injector=Injector)
class ServiceCommand(CommandBase):
    def _setup(self, parsed_arguments):
        for handler in self.handlers:
            self.broker.register_handler(handler)

    def _execute(self, parsed_arguments):
        """
        Returns a deferred that will never fire.
        """
        deferred = defer.Deferred()
        return deferred
