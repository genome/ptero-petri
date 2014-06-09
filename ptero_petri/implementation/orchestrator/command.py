from injector import inject
from ptero_petri.implementation import interfaces
from ptero_petri.implementation.orchestrator.handlers import PetriCreateTokenHandler
from ptero_petri.implementation.orchestrator.handlers import PetriNotifyPlaceHandler
from ptero_petri.implementation.orchestrator.handlers import PetriNotifyTransitionHandler


@inject(storage=interfaces.IStorage, broker=interfaces.IBroker,
        create_token_handler=PetriCreateTokenHandler,
        notify_place_handler=PetriNotifyPlaceHandler,
        notify_transition_handler=PetriNotifyTransitionHandler)
class OrchestratorCommand(object):
    def __init__(self):
        self.broker.register_handler(self.create_token_handler)
        self.broker.register_handler(self.notify_place_handler)
        self.broker.register_handler(self.notify_transition_handler)
