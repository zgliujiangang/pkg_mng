# /usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from patterns import singleton
import ConfigParser
import os


def read_config(file_name):
    config_path = os.path.join(os.path.dirname(__file__), "conf")
    file_name = os.path.join(config_path, file_name)
    config = ConfigParser.ConfigParser()
    with open(file_name) as f:
        config.readfp(f)
    return config


@singleton
def init_config():
    config = read_config("project.ini")
    return config


config = init_config()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.get("sqlite", "uri")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
#app.config["SQLALCHEMY_ECHO"] = True
app.secret_key = config.get("flask", "secret_key")
db = SQLAlchemy(app)