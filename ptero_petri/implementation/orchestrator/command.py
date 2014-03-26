from ..configuration.inject.broker import BrokerConfiguration
from ..configuration.inject.redis_conf import RedisConfiguration
from ..configuration.inject.service_locator import ServiceLocatorConfiguration
from .handlers import PetriCreateTokenHandler
from .handlers import PetriNotifyPlaceHandler
from .handlers import PetriNotifyTransitionHandler
from .service_command import ServiceCommand
import logging


LOG = logging.getLogger(__name__)


class OrchestratorCommand(ServiceCommand):
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
