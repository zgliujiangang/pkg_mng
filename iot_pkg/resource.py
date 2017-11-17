# -*- coding: utf-8 -*-


from iot_pkg.core import create_api
from iot_pkg.resources import user, file, proj, pkg, channel


def add_resource():
    api = create_api()
    # 用户注册、修改密码、获取基本信息接口
    api.add_resource(user.UserAPI, '/api/user')
    # 用户获取登录凭证、删除登录凭证接口
    api.add_resource(user.UserTokenAPI, '/api/user/token')
    # 文件上传下载接口
    api.add_resource(file.FileAPI, "/api/file", "/file/<file_id>")
    # 项目创建、删除、获取信息等接口
    api.add_resource(proj.ProjectAPI, "/api/project")
    api.add_resource(proj.ProjectListAPI, "/api/project/list")
    api.add_resource(proj.ProjectMsgAPI, "/api/project/msg/<uid>", endpoint="project_msg")
    api.add_resource(proj.ProjectFileAPI, "/api/project/download/<uid>", endpoint="project_download")
    # 安装包上传、获取、删除等接口
    api.add_resource(pkg.PackageAPI, "/api/package")
    api.add_resource(pkg.PackageListAPI, "/api/package/list")
    api.add_resource(pkg.PackageFileAPI, "/api/package/file", "/api/package/file/<fid>", endpoint='package_download')
    # 项目渠道创建、修改、删除接口
    api.add_resource(channel.ChannleListAPI, '/api/channel/list')
    api.add_resource(channel.ChannelAPI, '/api/channel')
