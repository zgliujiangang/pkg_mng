# -*- coding: utf-8 -*-


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_restful as restful
from iot_pkg.utils.cache import memoize, PickleCache
from iot_pkg import settings


@memoize
def create_app():
    app = Flask(__name__)
    app.secret_key = settings.SECRET_KEY
    return app


@memoize
def create_api():
    app = create_app()
    api = restful.Api(app)
    return api


@memoize
def create_db():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    db = SQLAlchemy(app)
    return db


@memoize
def create_cache():
    cache = PickleCache(settings.CACHE_PATH)
    return cache


app = create_app()
api = create_api()
db = create_db()
cache = create_cache()
