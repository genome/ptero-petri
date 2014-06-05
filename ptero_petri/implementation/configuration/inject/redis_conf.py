from ... import interfaces
from ..settings.injector import setting
import injector
import os
import redis
import subprocess
import sys
import tempfile
import time


class RedisConfiguration(injector.Module):
    @injector.singleton
    @injector.provides(interfaces.IStorage)
    @injector.inject(host=setting('PTERO_PETRI_REDIS_HOST', None),
            port=setting('PTERO_PETRI_REDIS_PORT', 6379),
            path=setting('PTERO_PETRI_REDIS_PATH', None))
    def provide_redis(self, host, port,  path):
        if path:
            return redis.Redis(unix_socket_path=path)
        else:
            return redis.Redis(host=host, port=port)
