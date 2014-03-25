from ...orchestrator.service_interface import OrchestratorServiceInterface
from ... import interfaces
import injector


class OrchestratorConfiguration(injector.Module):
    @injector.provides(interfaces.IOrchestrator)
    def provide_broker(self):
        return self.__injector__.get(OrchestratorServiceInterface)
