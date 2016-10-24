# /usr/bin/env python
# -*- coding: utf-8 -*-


from functools import wraps


def singleton(cls):
    # 单例模式 可用于类也可用于函数
    cls_instance = {}
    @wraps(cls)
    def instance(*args, **kwargs):
        if cls not in cls_instance:
            cls_instance[cls] = cls(*args, **kwargs)
        return cls_instance[cls]
    return instance