# /usr/bin/env python
# -*- coding: utf-8 -*-


from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import session
from functools import wraps
from werkzeug import check_password_hash
from models.user import User


def login_required(func):
	@wraps(func)
	def decorator(*args, **kwargs):
		username = session.get("username")
		if username:
			user = User.query.filter_by(name=username).first()
			if user is None:
				return redirect(url_for("login"))
			else:
				request.user = user
				return func(*args, **kwargs)
		else:
			return redirect(url_for("login"))
	return decorator


@login_required
def index():
	# 首页
	# 目前跳转到程序包首页
	return render_template("index.html")


def login():
	# 登录页
	if request.method.lower() == "get":
		return render_template("login.html")
	else:
		username = request.form.get("username")
		password = request.form.get("password")
		user = User.query.filter_by(name=username).first()
		if user is None:
			flash("用户不存在")
			return redirect(url_for("login"))
		else:
			check = check_password_hash(user.password, password)
			if check:
				session["username"] = username
				return redirect(url_for("index"))
			else:
				flash("密码错误")
				return redirect(url_for("login"))


@login_required
def logout():
	# 登出页
	session.pop("username", None)
	return redirect(url_for("login"))