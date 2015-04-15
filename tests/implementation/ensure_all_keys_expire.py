import os
import redis
from unittest import TestCase, main


class TestAllKeysExpire(TestCase):

    def setUp(self):
        self.connection = redis.StrictRedis(
            host=os.environ['PTERO_PETRI_REDIS_HOST'],
            port=os.environ['PTERO_PETRI_REDIS_PORT'])

    def test_all_keys_expire(self):
        unexpired_keys = set()
        for key in self.connection.keys('*'):
            if self.connection.ttl(key) == -1:
                unexpired_keys.add(key)
        self.assertEqual(unexpired_keys, set())

if __name__ == "__main__":
    main()
