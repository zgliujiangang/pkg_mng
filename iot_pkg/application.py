# -*- coding: utf-8 -*-


import sys; sys.path.append("..")
from iot_pkg.views import user
from iot_pkg._global import app, api, db


def add_resource():
    api.add_resource(user.UserAPI, '/user')
    api.add_resource(user.UserTokenAPI, '/user/token')
    return api


add_resource()


if __name__ == '__main__':
    app.run(debug=True)