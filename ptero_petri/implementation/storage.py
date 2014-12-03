import os
import redis


__all__ = ['get_connection']


_HOST = os.environ.get('PTERO_PETRI_REDIS_HOST')
_PASSWORD = os.environ.get('PTERO_PETRI_REDIS_PASSWORD')
_PORT = int(os.environ.get('PTERO_PETRI_REDIS_PORT', 6379))
_SOCKET_PATH = os.environ.get('PTERO_PETRI_REDIS_PATH')


def get_connection():
    if _SOCKET_PATH:
        return redis.Redis(unix_socket_path=_SOCKET_PATH, password=_PASSWORD)

    else:
        return redis.Redis(host=_HOST, port=_PORT, password=_PASSWORD)
