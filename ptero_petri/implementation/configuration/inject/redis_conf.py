from ... import interfaces
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
    def provide_redis(self):
        if self.path:
            return redis.Redis(unix_socket_path=self.path,
                    password=self.password)
        else:
            return redis.Redis(host=self.host, port=self.port,
                    password=self.password)

    @property
    def password(self):
        return os.environ.get('PTERO_PETRI_REDIS_PASSWORD')

    @property
    def host(self):
        return os.environ.get('PTERO_PETRI_REDIS_HOST')

    @property
    def port(self):
        return int(os.environ.get('PTERO_PETRI_REDIS_PORT', 6379))

    @property
    def path(self):
        return os.environ.get('PTERO_PETRI_REDIS_PATH')
