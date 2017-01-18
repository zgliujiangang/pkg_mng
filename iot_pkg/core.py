# -*- coding: utf-8 -*-


from flask import Flask, request
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_restful_swagger import swagger
from iot_pkg import settings
from iot_pkg.utils.cache import memoize, PickleCache


@memoize
def create_app():
    app = Flask(__name__)
    app.secret_key = settings.SECRET_KEY
    @app.before_request
    def before_request():
        if request.headers.get('Protocol') == 'https':
            settings.DOMAIN = 'https://update.useonline.cn'
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', settings.ACCESS_CONTROL)
        response.headers.add('Access-Control-Allow-Headers', request.headers.get('Access-Control-Request-Headers'))
        response.headers.add('Access-Control-Allow-Methods', request.headers.get('Access-Control-Request-Method'))
        response.headers.add('Access-Control-Max-Age', 86400)
        return response
    return app


@memoize
def create_api():
    app = create_app()
    api = Api(app)
    api = swagger.docs(api, apiVersion='1.0',
                       basePath=settings.SWAGGER_BASE_PATH,
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
