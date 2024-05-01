#!/usr/bin/env python3
""" lists all documents in a collection
"""
import pymongo


def list_all(mongo_collection):
    """ function that lists all documents in a collection
    """
    if mongo_collection is None:
        return []
    documents = mongo_collection.find()
    return [post for post in documents]
