# -*- coding: utf-8 -*-


import os
import ConfigParser
from .cache import memoize


@memoize
def parse_ini_config(file_name):
    config = ConfigParser.ConfigParser()
    with open(file_name) as f:
        config.readfp(f)
    return config


@memoize
def parse_yaml_config(file_name):
    pass


@memoize
def parse_xml_config(file_name):
    pass