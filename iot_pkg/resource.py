# -*- coding: utf-8 -*-


from iot_pkg.core import create_api
from iot_pkg.resources import user, file, proj, pkg


def add_resource():
    api = create_api()
    # 用户注册、修改密码、获取基本信息接口
    api.add_resource(user.UserAPI, '/user')
    # 用户获取登录凭证、删除登录凭证接口
    api.add_resource(user.UserTokenAPI, '/user/token')
    # 文件上传下载接口
    api.add_resource(file.FileAPI, "/file", "/file/<file_id>")
    # 项目创建、删除、获取信息等接口
    api.add_resource(proj.ProjectAPI, "/project")
    api.add_resource(proj.ProjectListAPI, "/project/list")
    api.add_resource(proj.ProjectMsgAPI, "/project/msg/<uid>", endpoint="project_msg")
    api.add_resource(proj.ProjectFileAPI, "/project/download/<uid>", endpoint="project_download")
    # 安装包上传、获取、删除等接口
    api.add_resource(pkg.PackageAPI, "/package")
    api.add_resource(pkg.PackageListAPI, "/package/list")
    api.add_resource(pkg.PackageFileAPI, "/package/file", "/package/file/<fid>", endpoint='package_download')