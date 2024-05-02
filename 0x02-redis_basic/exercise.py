#!/usr/bin/env python3
""" Module for caching data using Redis
"""
from functools import wraps
import redis
from redis import Redis
from typing import Callable, Union
import uuid


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


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        input = str(args)
        self._redis.rpush(f"{method.__qualname__}:inputs", input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(f"{method.__qualname__}:outputs", output)
        return output
    return wrapper


def replay(method: Callable):
    """Display the history of calls of a particular function"""
    method_name = method.__qualname__
    inputs_key = f"{method_name}:inputs"
    outputs_key = f"{method_name}:outputs"
    redis_conn = redis.Redis()
    try:
        inputs = redis_conn.lrange(inputs_key, 0, -1)
        outputs = redis_conn.lrange(outputs_key, 0, -1)
    except redis.exceptions.RedisError as e:
        print(f"Failed to retrieve history from Redis: {e}")
        return
    print(f"{method_name} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        inp_str = inp.decode("utf-8")
        out_str = out.decode("utf-8")
        print(f"{method_name}(*{inp_str}) -> {out_str}")


class Cache:
    """A class for caching data using Redis
    """
    def __init__(self):
        """Cache constructor
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
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
