# /usr/bin/env python
# -*- coding: utf-8 -*-

import platform
import ConfigParser
import os


def read_config(file_name):
    config_path = os.path.join(os.path.dirname(__file__), "conf")
    file_name = os.path.join(config_path, file_name)
    config = ConfigParser.ConfigParser()
    with open(file_name) as f:
        config.readfp(f)
    return config


def save_config(file_name, config):
    config_path = os.path.join(os.path.dirname(__file__), "conf")
    file_name = os.path.join(config_path, file_name)
    with open(file_name, "wb") as f:
        config.write(f)
    return config


def init_config():
    user_file = "users.ini"
    user_config = read_config(user_file)
    current_user = platform.node()
    init_file = user_config.get("users", current_user)
    config = read_config(init_file)
    return config
