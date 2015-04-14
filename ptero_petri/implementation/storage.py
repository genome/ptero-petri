import os
import redis


__all__ = ['get_connection']


_HOST = os.environ.get('PTERO_PETRI_REDIS_HOST')
_PASSWORD = os.environ.get('PTERO_PETRI_REDIS_PASSWORD')
_PORT = int(os.environ.get('PTERO_PETRI_REDIS_PORT', 6379))
_SOCKET_PATH = os.environ.get('PTERO_PETRI_REDIS_PATH')

DEFAULT_TTL = int(os.environ['PTERO_PETRI_REDIS_DEFAULT_TTL'])
COMMANDS_THAT_CAN_ADD_KEYS = set(['lpush', 'rpush', 'set', 'setnx',
        'incr', 'decr', 'incrby', 'decrby', 'hincrby', 'hset',
        'hsetnx', 'hmset', 'sadd'])

class ExpiringConnection(object):
    def __init__(self, connection, default_ttl):
        self.connection = connection
        self.default_ttl = default_ttl

    def __getattr__(self, name):
        if name in COMMANDS_THAT_CAN_ADD_KEYS:
            def wrapper(key, *args, **kwargs):
                rv = getattr(self.connection, name)(key, *args, **kwargs)
                if rv and not self.connection.expire(key, self.default_ttl):
                    raise RunTimeError(
                        "Failed to set expriration of key %s to %s seconds" %
                        key, self.default_ttl)
                return rv
            return wrapper
        else:
            return getattr(self.connection, name)


def get_connection():
    if _SOCKET_PATH:
        return ExpiringConnection(connection=redis.Redis(
            unix_socket_path=_SOCKET_PATH, password=_PASSWORD),
            default_ttl=DEFAULT_TTL)

    else:
        return ExpiringConnection(connection=redis.Redis(
            host=_HOST, port=_PORT, password=_PASSWORD),
            default_ttl=DEFAULT_TTL)
