# -*- coding:utf-8 -*-


from sqlalchemy.exc import IntegrityError
from flask_restful import request, Resource, reqparse
from flask_restful_swagger import swagger
from iot_pkg import settings
from iot_pkg.core import create_db
from iot_pkg.contrib.session import Session
from iot_pkg.contrib.crypto import PasswordCrypto
from iot_pkg.contrib.auth import login_required
from iot_pkg.models.user import User


db = create_db()


class UserAPI(Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("email", type=str, required=True)
    post_parser.add_argument("password", type=str, required=True)
    post_parser.add_argument("password_again", type=str, required=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("old_pwd", type=str, required=True)
    put_parser.add_argument("new_pwd", type=str, required=True)
    put_parser.add_argument('new_pwd_again', type=str, required=True)

    @swagger.operation(
        notes='获取用户信息',
        summary='获取用户信息',
        nickname='get',
        parameters=[
            {
            "name": settings.USER_SESSION_KEY,
            "description": "登录凭证",
            'required': True,
            'dataType': 'string',
            'paramType': 'header'
            }
        ])
    @login_required
    def get(self):
        # 用户基本信息
        data = request.user.to_dict()
        return {"code": "200", "msg": "获取信息成功", "data": data}

    @swagger.operation(
        notes='用户注册',
        summary='用户注册',
        nickname='post',
        parameters=[
            {
                "name": "email",
                "description": "注册邮箱",
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                "name": 'password',
                'description': "密码",
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'password_again',
                'description': '确认密码',
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        # 用户注册
        args = self.post_parser.parse_args()
        email = args["email"]
        password = args["password"]
        password_again = args["password_again"]
        if password != password_again:
            return {"code": "400", "msg": "两次密码不一致"}
        pwd_hash = PasswordCrypto.hash(password)
        user = User(email, pwd_hash)
        try:
            db.session.add(user)
            db.session.commit()
            return {"code": "200", "msg": "注册成功"}
        except IntegrityError:
            return {"code": "203", "msg": "该邮箱已被注册"}
        except Exception as e:
            print str(e)
            return {"code": "500", "msg": "程序出错，请联系开发人员"}

    @swagger.operation(
        notes='修改密码',
        summary='修改密码',
        nickname='put',
        parameters=[
            {
                "name": settings.USER_SESSION_KEY,
                "description": "登录凭证",
                'required': True,
                'dataType': 'string',
                'paramType': 'header'
            },
            {
                'name': 'old_pwd',
                'description': '旧密码',
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'new_pwd',
                'description': '新密码',
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'new_pwd_again',
                'description': '确认新密码',
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    @login_required
    def put(self):
        # 修改密码
        args = self.put_parser.parse_args()
        old_pwd = args["old_pwd"]
        new_pwd = args["new_pwd"]
        new_pwd_again = args['new_pwd_again']
        if new_pwd != new_pwd_again:
            return {"code": "400", "msg": "两次新密码不一致"}
        user = request.user
        if PasswordCrypto.check(user.password, old_pwd):
            user.password = PasswordCrypto.hash(new_pwd)
            db.session.commit()
            user_session_id = getattr(request, settings.USER_SESSION_KEY)
            Session.delete(user_session_id)
            return {"code": "200", "msg": "密码修改成功，请重新登录"}
        else:
            return {"code": "400", "msg": "密码错误"}


class UserTokenAPI(Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("email", type=str, required=True)
    post_parser.add_argument("password", type=str, required=True)

    @swagger.operation(
        notes='用户登录（获取登录凭证）',
        summary='用户登录（获取登录凭证）',
        nickname='post',
        parameters=[
            {
                "name": "email",
                "description": "注册邮箱",
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                "name": 'password',
                'description': "密码",
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        # 登录接口
        args = self.post_parser.parse_args()
        email = args["email"]
        password = args["password"]
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"code": "404", "msg": "用户不存在"}
        if PasswordCrypto.check(user.password, password):
            # 用户身份验证成功
            user_session_id = Session.set(user, settings.USER_SESSION_TIMEOUT)
            data = {settings.USER_SESSION_KEY: user_session_id}
            return {"code": "200", "msg": "登录成功", "data": data}
        else:
            return {"code": "403", "msg": "邮箱或密码错误"}

    @swagger.operation(
        notes='用户登出（删除登录凭证）',
        summary='用户登出（删除登录凭证）',
        nickname='get',
        parameters=[
            {
                "name": settings.USER_SESSION_KEY,
                "description": "登录凭证",
                'required': True,
                'dataType': 'string',
                'paramType': 'header'
            }
        ])
    @login_required
    def delete(self):
        # 登出接口
        user_session_id = getattr(request, settings.USER_SESSION_KEY)
        Session.delete(user_session_id)
        return {"code": "200", "msg": "登出成功"}