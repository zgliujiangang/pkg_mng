# -*- coding: utf-8 -*-


import functools
from flask_restful import request
from iot_pkg.settings import USER_SESSION_KEY
from iot_pkg.contrib.session import Session
from iot_pkg.core import create_db


db = create_db()


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_session_id = request.values.get(USER_SESSION_KEY) or \
         request.cookies.get(USER_SESSION_KEY) or \
         request.headers.get(USER_SESSION_KEY)
        if not user_session_id:
            return {"code": "401", "msg": "Unauthorized"}
        user = Session.get(user_session_id)
        if not user:
            Session.delete(user_session_id)
            return {"code": "401", "msg": "Unauthorized"}
        setattr(request, USER_SESSION_KEY, user_session_id)
        user = db.session.merge(user)
        request.user = user
        return func(*args, **kwargs)
    return wrapper