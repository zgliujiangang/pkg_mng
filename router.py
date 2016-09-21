# /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

reload(sys)
# 设置项目编码
sys.setdefaultencoding("utf-8")
# 将项目的启动路径添加到python解释器的搜索路径列表中
sys.path.append(".")


from views.proj import proj_index, proj_add, proj_delete, proj_latest_msg, proj_latest_download
from views.pkg import pkg_index, pkg_add, pkg_info, pkg_public, pkg_delete, pkg_download
from views.user import user_index, user_add, user_delete
from views.common import index, login, logout
from _global import app, db


# 项目管理
app.add_url_rule("/proj", view_func=proj_index, methods=["get"])
app.add_url_rule("/proj/add", view_func=proj_add, methods=["get", "post"])
app.add_url_rule("/proj/delete", view_func=proj_delete, methods=["get"])
app.add_url_rule("/proj/<proj_name>/msg", view_func=proj_latest_msg, methods=["get"])
app.add_url_rule("/proj/<proj_name>/download", view_func=proj_latest_download, methods=["get"])

# 程序包管理
app.add_url_rule("/pkg", view_func=pkg_index, methods=["get"])
app.add_url_rule("/pkg/add", view_func=pkg_add, methods=["post"])
app.add_url_rule("/pkg/info", view_func=pkg_info, methods=["get", "post"])
app.add_url_rule("/pkg/public", view_func=pkg_public, methods=["get"])
app.add_url_rule("/pkg/delete", view_func=pkg_delete, methods=["get"])
app.add_url_rule("/pkg/download/<pkg_name>", view_func=pkg_download, methods=["get"])

# 后台用户管理
app.add_url_rule("/user", view_func=user_index, methods=["get"])
app.add_url_rule("/user/add", view_func=user_add, methods=["post"])
app.add_url_rule("/user/delete", view_func=user_delete, methods=["get"])

# 登录登出和首页
app.add_url_rule("/", view_func=index, methods=["get"])
app.add_url_rule("/login", view_func=login, methods=["get", "post"])
app.add_url_rule("/logout", view_func=logout, methods=["get"])