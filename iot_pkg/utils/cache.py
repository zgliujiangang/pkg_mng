# -*- coding: utf-8 -*-


import os
import time
import abc
from decorator import decorate
try:
    import cPickle as pickle
except ImportError:
    import pickle


class BaseCache(object):
    # 缓存的抽象基类
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def set(self, key, value, expires_in=None):
        pass

    @abc.abstractmethod
    def get(self, key):
        pass

    @abc.abstractmethod
    def delete(self, key):
        pass


class PickleCacheData:
    # 序列化缓存数据类

    def __init__(self, key, value, expires_in=None):
        self._key = key
        self._value = value
        self._expires_in = expires_in
        self.create_time = time.time()

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        if self._expires_in is None:
            return self._value
        elif time.time() >= self.create_time + self._expires_in:
            return None
        else:
            return self._value


class PickleCache(BaseCache):
    # 序列化缓存, 适用单点服务缓存，多点服务实例请使用redis、memcache等专业缓存工具

    def __init__(self, cache_dir):
        assert cache_dir is not None, "cache_dir不能为None"
        assert os.path.isdir(cache_dir), "cache_dir:%s必须是一个有效的目录" % cache_dir
        self.cache_dir = cache_dir

    def set(self, key, value, expires_in=None):
        data = PickleCacheData(key, value, expires_in)
        cache_file = os.path.join(self.cache_dir, data.key)
        with open(cache_file, "w") as f:
            pickle.dump(data, f)

    def get(self, key):
        cache_file = os.path.join(self.cache_dir, key)
        if not os.path.exists(cache_file):
            return None
        else:
            with open(cache_file) as f:
                data = pickle.load(f)
            return data.value

    def delete(self, key):
        cache_file = os.path.join(self.cache_dir, key)
        if os.path.exists(cache_file):
            os.remove(cache_file)


def _memoize(func, *args, **kwargs):
    if kwargs:
        key = args, frozenset(kwargs.items())
    else:
        key = args
    cache = func.cache
    if key not in cache:
        cache[key] = func(*args, **kwargs)
    return cache[key]


def memoize(func):
    # 函数计算结果缓存装饰器
    func.cache = {}
    return decorate(func, _memoize)