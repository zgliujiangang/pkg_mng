# /usr/bin/env python
# -*- coding: utf-8 -*-


import ConfigParser
import os


def read_config(file_name):
    config_path = os.path.join(os.path.dirname(__file__), "conf")
    file_name = os.path.join(config_path, file_name)
    config = ConfigParser.ConfigParser()
    with open(file_name) as f:
        config.readfp(f)
    return config


def init_config():
    config = read_config("project.ini")
    return config
