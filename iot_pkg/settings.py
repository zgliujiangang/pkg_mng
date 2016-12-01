# -*- coding: utf-8 -*-


from utils.config import parse_ini_config


config = parse_ini_config("conf/project.ini")


SQLALCHEMY_DATABASE_URI = config.get("sqlite", "uri")
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = "ldolHUK$*21KHLioefd*&1io"
AUTH_TOKEN_KEY = "access_token"
AUTH_TOKEN_TIMEOUT = 60 * 3
CACHE_PATH = '/Users/admin/Project/iot_pkg/cache_dir'