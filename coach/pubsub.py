"""
Provides a interface for Redis PubSub
"""

from redis import Redis

from coach.constants import constants
from coach.utils import load_env_as_type


class Broker:
    """
    Wrapper for the Redis PubSub object
    """

    def __init__(self, host=None, port=None, db=None, password=None):
        host = host or load_env_as_type(
            constants.REDIS_HOST_ENV.value, str, constants.REDIS_HOST_ENV_DEFAULT.value
        )
        port = port or load_env_as_type(
            constants.REDIS_PORT_ENV.value, int, constants.REDIS_PORT_ENV_DEFAULT.value
        )
        db = db or load_env_as_type(
            constants.REDIS_DB_ENV.value, int, constants.REDIS_DB_ENV_DEFAULT.value
        )
        password = password or load_env_as_type(
            constants.REDIS_PASSWORD_ENV.value,
            str,
            constants.REDIS_PASSWORD_ENV_DEFAULT.value,
        )
        self._redis = Redis(host=host, port=port, db=db, password=password)

    def publish(self, channel, message):
        """
        Publish a message to a channel
        """
        self._redis.publish(channel, message)

    def subscribe(self, channel, handler=None):
        """
        Subscribe to a channel
        """
        pubsub = self._redis.pubsub()
        if handler:
            pubsub.subscribe(**{channel: handler})
        else:
            pubsub.subscribe(channel)
        return pubsub

    def run_in_thread(self, channel, handler, sleep_time=0.001):
        """
        Run handler for a channel in a thread
        """
        pubsub = self.subscribe(channel, handler)
        pubsub.run_in_thread(sleep_time=sleep_time)
