from ..rom import get_object
import celery


__all__ = ['CreateToken']


class CreateToken(celery.Task):
    ignore_result = True

    def run(self, net_key, place_idx=None, place_name=None, color=None,
            color_group_idx=None, data=None):
        if data is None:
            data = {}

        from .. import storage
        net = get_object(storage.connection, net_key)

        if place_idx is None:
            place_idx = net.place_lookup[place_name]

        if color is None:
            color_group = net.add_color_group(1)
            color = color_group.begin
            color_group_idx = color_group.idx

        return net.create_put_notify(place_idx, color=color,
                color_group_idx=color_group_idx, data=data)
