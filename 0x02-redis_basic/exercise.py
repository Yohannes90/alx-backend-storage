#!/usr/bin/env python3
""" Module for caching data using Redis
"""
import uuid
import redis
from typing import Callable, Union
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """ Count the number of times a method is called
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapper function
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    """A class for caching data using Redis
    """
    def __init__(self):
        """Cache constructor
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Callable = None) -> Union[str, bytes, int, float, None]:
        """ Get data from Redis
        """
        if fn:
            data = self._redis.get(key)
            if data is None:
                return None
            return fn(data)
        else:
            return self._redis.get(key)

    def get_str(self, key: str) -> Union[str, None]:
        """ Retrieve a string value from based on the given key
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Union[int, None]:
        """ Retrieve an int value from Redis based on the given key
        """
        return self.get(key, fn=int)
