# -*- coding: utf-8 -*-


try:
    import cPickle as pickle
except ImportError:
    import pickle
import uuid
from iot_pkg.core import create_cache


cache = create_cache()


class Session(object):

    @staticmethod
    def set(obj, timeout=None):
        # return a session_id
        session_id = str(uuid.uuid4())
        cache.set(session_id, pickle.dumps(obj), timeout)
        return session_id

    @staticmethod
    def get(session_id):
        # return the cache object
        obj = cache.get(session_id)
        obj = pickle.loads(obj) if obj else obj
        return obj

    @staticmethod
    def delete(session_id):
        cache.delete(session_id)
        return True

    @classmethod
    def test_case(cls):
        obj = "session test"
        session_id = cls.set(obj)
        assert obj == cls.get(session_id), "session缓存方法有误"
        cls.delete(session_id)