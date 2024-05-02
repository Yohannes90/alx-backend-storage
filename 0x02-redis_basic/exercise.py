#!/usr/bin/env python3
""" Module for caching data using Redis
"""
import uuid
import redis
from typing import Union


class Cache:
    """A class for caching data using Redis
    """
    def __init__(self):
        """Cache constructor
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
