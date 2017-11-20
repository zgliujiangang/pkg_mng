# -*- coding: utf-8 -*-


# 数据库连接参数，需重写
SQLALCHEMY_DATABASE_URI = None
SQLALCHEMY_TRACK_MODIFICATIONS = True

# flask session加密key
SECRET_KEY = "ldolHUK$*21KHLioefd*&1io"

# 用户认证的令牌key以及有效期限
USER_SESSION_KEY = "access_token"
USER_SESSION_TIMEOUT = 60 * 3

# 用户缓存数据的系统路径，需重写
CACHE_PATH = None

# 用户存放上传文件的路径，需重写
FILE_PATH = None
DOMAIN = ''
