from .. import webhooks
from .base import BasicActionBase
from .merge import MergeMixin
from ptero_common import nicer_logging


LOG = nicer_logging.getLogger(__name__)


class NotifyAction(BasicActionBase, MergeMixin):

    def execute(self, net, color_descriptor, active_tokens):
        cd = color_descriptor
        new_token = self.get_merged_token(net, color=cd.color,
                                          color_group_idx=cd.group.idx,
                                          active_tokens=active_tokens)

        data = {'net_key': net.key}
        data.update(color_descriptor.as_dict)

        LOG.info("Sending Webhook for net <%s> -- %s",
                net.key, self.notify_url,
                extra={'netKey': net.key})
        webhooks.send_webhook(
            url=self.notify_url,
            response_data={
                'color_descriptor': cd,
                'net_key': net.key,
                'response_places': self.response_places,
            },
            data=data)

        return [new_token]

    @property
    def notify_url(self):
        return self.args['url']
