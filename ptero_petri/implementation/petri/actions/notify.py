from .. import webhooks
from ...container_utils import head
from .base import BasicActionBase
from .merge import MergeMixin
from twisted.internet import defer


class NotifyAction(BasicActionBase, MergeMixin):
    def execute(self, net, color_descriptor, active_tokens, service_interfaces):
        new_token = self.get_merged_token(net, color_descriptor, active_tokens)

        data = None
        if 'requested_data' in self.args:
            data = {
                'requested_data': self.args['requested_data']
            }

        webhooks.send_webhook(
                url=self.notify_url,
                response_data={
                    'color_descriptor': color_descriptor,
                    'net_key': net.key,
                    'response_places': self.response_places,
                },
                data=color_descriptor.as_dict)

        return [new_token], defer.succeed(None)

    @property
    def notify_url(self):
        return self.args['url']
