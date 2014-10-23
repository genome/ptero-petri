import os
import redis


__all__ = ['connection']


_HOST = os.environ.get('PTERO_PETRI_REDIS_HOST')
_PASSWORD = os.environ.get('PTERO_PETRI_REDIS_PASSWORD')
_PORT = int(os.environ.get('PTERO_PETRI_REDIS_PORT', 6379))
_SOCKET_PATH = os.environ.get('PTERO_PETRI_REDIS_PATH')


if _SOCKET_PATH:
    connection = redis.Redis(unix_socket_path=_SOCKET_PATH,
            password=_PASSWORD)

else:
    connection = redis.Redis(host=_HOST, port=_PORT,
            password=_PASSWORD)
