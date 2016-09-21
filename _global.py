# /usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from conf_injection import init_config


config = init_config()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.get("sqlite", "uri")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
#app.config["SQLALCHEMY_ECHO"] = True
app.secret_key = config.get("flask", "secret_key")
db = SQLAlchemy(app)