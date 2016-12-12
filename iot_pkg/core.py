# -*- coding: utf-8 -*-


from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_restful_swagger import swagger
from iot_pkg import settings
from iot_pkg.utils.cache import memoize, PickleCache


@memoize
def create_app():
    app = Flask(__name__)
    app.secret_key = settings.SECRET_KEY
    return app


@memoize
def create_api():
    app = create_app()
    api = Api(app)
    api = swagger.docs(api, apiVersion='1.0',
                       basePath='http://localhost:5000',
                       resourcePath='/',
                       produces=['text/html'],
                       api_spec_url='/api/doc',
                       description='安装包系统API文档')
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
