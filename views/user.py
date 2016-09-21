# /usr/bin/env python
# -*- coding:utf-8 -*-

from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash
from werkzeug import generate_password_hash
from models.user import User
from _global import db
from _global import app
from common import login_required


@login_required
def user_index():
	# 用户列表
	user_query = User.query.order_by(User.id.desc())
	page = request.args.get("page") or 1
	per_page = request.args.get("per_page") or 20
	try:
		page, per_page = int(page), int(per_page)
	except ValueError:
		page, per_page = 1, 20
	limit = per_page
	offset = (page - 1) * per_page
	if request.args.get("username"):
		user_query = user_query.filter(User.name.ilike("%" + request.args.get("username") +"%"))
	user_list = user_query.offset(offset).limit(limit).all()
	user_count = user_query.count()
	page_count = user_count / per_page + 1 if user_count % per_page else user_count / per_page
	return render_template("user_list.html", user_list=user_list, page_count=page_count, page=page)


@login_required
def user_add():
	# 用户增改
	user_id = request.form.get("user_id")
	username = request.form.get("username")
	password = request.form.get("password")
	if not username or not password:
		flash("缺少参数")
		return redirect(url_for("user_index"))
	pwd_hash = generate_password_hash(password)
	if user_id:
		try:
			User.query.filter_by(id=user_id).update({User.name: username, User.password: pwd_hash})
			db.session.commit()
			flash("修改用户成功")
		except Exception as e:
			flash("修改用户失败")
		finally:
			return redirect(url_for("user_index"))
	else:
		user = User(username, pwd_hash)
		try:
			db.session.add(user)
			db.session.commit()
			flash("添加用户成功")
		except Exception as e:
			flash("添加用户失败")
		finally:
			return redirect(url_for("user_index"))


@login_required
def user_delete():
	# 用户删除
	user_id = request.args.get("user_id")
	user = User.query.filter_by(id=user_id).first_or_404()
	db.session.delete(user)
	db.session.commit()
	flash("删除用户(%s)成功" % user)
	return redirect(url_for("user_index"))