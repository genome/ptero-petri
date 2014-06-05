from .. import interfaces
from .messages import CreateTokenMessage, NotifyPlaceMessage
from .messages import NotifyTransitionMessage
from injector import inject
import logging


LOG = logging.getLogger(__name__)


EXCHANGE_NAME = 'ptero'


@inject(broker=interfaces.IBroker)
class OrchestratorServiceInterface(interfaces.IOrchestrator):
    def create_token(self, net_key, place_idx,
            color, color_group_idx, data=None):
        message = CreateTokenMessage(net_key=net_key, place_idx=place_idx,
                color=color, color_group_idx=color_group_idx, data=data)
        return self.broker.publish(EXCHANGE_NAME, 'petri.place.create_token',
                message)

    def notify_place(self, net_key, place_idx, color):
        message = NotifyPlaceMessage(net_key=net_key, place_idx=place_idx,
                color=color)
        return self.broker.publish(EXCHANGE_NAME, 'petri.place.notify',
                message)

    def notify_transition(self, net_key, transition_idx, place_idx, token_idx):
        message = NotifyTransitionMessage(
                net_key=net_key,
                transition_idx=transition_idx,
                place_idx=place_idx,
                token_idx=token_idx)
        return self.broker.publish(EXCHANGE_NAME, 'petri.transition.notify',
                message)
