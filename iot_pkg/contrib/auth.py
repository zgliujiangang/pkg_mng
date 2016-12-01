# -*- coding: utf-8 -*-


import json
import functools
from flask_restful import request
from werkzeug import generate_password_hash, check_password_hash
from iot_pkg.settings import AUTH_TOKEN_KEY
from iot_pkg._global import cache
try:
    import cPickle as pickle
except ImportError:
    import pickle


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth_token = request.values.get(AUTH_TOKEN_KEY) or \
         request.cookies.get(AUTH_TOKEN_KEY)
        if not auth_token:
            return {"code": "403", "msg": "Anauthorization"}
        user = cache.get(auth_token)
        if not user:
            cache.delete(auth_token)
            return {"code": "403", "msg": "Anauthorization"}
        setattr(request, AUTH_TOKEN_KEY, auth_token)
        request.user = pickle.loads(user)
        return func(*args, **kwargs)
    return wrapper


def hash_password(pwd):
    return generate_password_hash(pwd)


def check_password(hash_pwd, pwd):
    return check_password_hash(hash_pwd, pwd)