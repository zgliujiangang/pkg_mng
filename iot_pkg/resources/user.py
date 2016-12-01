# -*- coding:utf-8 -*-


try:
    import cPickle as pickle
except ImportError:
    import pickle
import uuid
import sqlite3
from flask_restful import request, Resource, reqparse
from iot_pkg import settings
from iot_pkg._global import db, cache
from iot_pkg.models.user import User
from iot_pkg.contrib import auth


class UserAPI(Resource):

	post_parser = reqparse.RequestParser()
	post_parser.add_argument("email", type=str, required=True)
	post_parser.add_argument("password", type=str, required=True)

	put_parser = reqparse.RequestParser()
	put_parser.add_argument("old_pwd", type=str, required=True)
	put_parser.add_argument("new_pwd", type=str, required=True)

	@auth.login_required
	def get(self):
		# 用户基本信息
		data = request.user.to_dict()
		return {"code": "200", "msg": "获取信息成功", "data": data}

	def post(self):
		# 用户注册
		args = self.post_parser.parse_args()
		email = args["email"]
		password = args["password"]
		pwd_hash = auth.hash_password(password)
		user = User(email, pwd_hash)
		try:
			db.session.add(user)
			db.session.commit()
			return {"code": "200", "msg": "注册成功"}
		except sqlite3.IntegrityError:
			return {"code": "203", "msg": "该邮箱已被注册"}
		except Exception:
			return {"code": "500", "msg": "程序出错，请联系开发人员"}

	@auth.login_required
	def put(self):
		# 修改密码
		args = self.put_parser.parse_args()
		old_pwd = args["old_pwd"]
		new_pwd = args["new_pwd"]
		user = request.user
		if auth.check_password(user.password, old_pwd):
			user.password = auth.hash_password(new_pwd)
			db.session.add(user)
			db.session.commit()
			cache.delete(getattr(request, settings.AUTH_TOKEN_KEY))
			return {"code": "200", "msg": "密码修改成功，请重新登录"}
		else:
			return {"code": "400", "msg": "密码错误"}


class UserTokenAPI(Resource):

	post_parser = reqparse.RequestParser()
	post_parser.add_argument("email", type=str, required=True)
	post_parser.add_argument("password", type=str, required=True)

	def post(self):
		# 登录接口
		args = self.post_parser.parse_args()
		email = args["email"]
		password = args["password"]
		user = User.query.filter_by(email=email).first()
		if not user:
			return {"code": "404", "msg": "用户不存在"}
		if auth.check_password(user.password, password):
			# 用户身份验证成功
			token = str(uuid.uuid4())
			cache.set(token, pickle.dumps(user), settings.AUTH_TOKEN_TIMEOUT)
			data = {settings.AUTH_TOKEN_KEY: token}
			return {"code": "200", "msg": "登录成功", "data": data}
		else:
			return {"code": "403", "msg": "邮箱或密码错误"}

	@auth.login_required
	def delete(self):
		# 登出接口
		token = getattr(request, settings.AUTH_TOKEN_KEY)
		cache.delete(token)
		return {"code": "200", "msg": "登出成功"}