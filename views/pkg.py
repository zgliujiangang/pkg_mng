# /usr/bin/env python
# -*- coding:utf-8 -*-

import json
import os
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash
from flask import send_file
from flask import abort
from _global import db, config, app
from models.pkg import Package
from models.proj import Project
from common import login_required


@login_required
def pkg_index():
	# 程序包首页
	page = request.args.get("page") or 1
	per_page = request.args.get("per_page") or 20
	try:
		page, per_page = int(page), int(per_page)
	except ValueError:
		page, per_page = 1, 20
	limit = per_page
	offset = (page - 1) * per_page
	proj_list = Project.query.all()
	pkg_query = Package.query.order_by(Package.id.desc())
	if request.args.get("proj_id"):
		pkg_query = pkg_query.filter_by(project_id=request.args.get("proj_id"))
	if request.args.get("version"):
		pkg_query = pkg_query.filter(Package.version.ilike("%" + request.args.get("version") + "%"))
	if request.args.get("name"):
		pkg_query = pkg_query.filter(Package.name.ilike("%" + request.args.get("version") + "%"))
	pkg_list = pkg_query.offset(offset).limit(limit).all()
	pkg_count = pkg_query.count()
	page_count = pkg_count / per_page + 1 if pkg_count % per_page else pkg_count / per_page
	return render_template("pkg_list.html", pkg_list=pkg_list, proj_list=proj_list, 
		page_count=page_count, page=page, pkg_cls=Package)


@login_required
def pkg_add():
	# 程序包增改
	pkg_id = request.form.get("pkg_id")
	if pkg_id:
		# 修改
		package = Package.query.filter_by(id=pkg_id).first_or_404()
		origin_path = os.path.join(config.get("flask", "pkg_path"), package.name)
		pkg_update = {}
		pkg_file = request.files.get("pkg_file")
		version = request.form.get("version")
		proj_id = request.form.get("proj_id")
		update_level = request.form.get("update_level")
		update_content = request.form.get("update_content")
		if pkg_file:
			pkg_update[Package.name] = pkg_file.filename
		if version:
			pkg_update[Package.version] = version
		if proj_id:
			pkg_update[Package.project_id] = proj_id
		if update_level:
			pkg_update[Package.update_level] = update_level
		if update_content:
			pkg_update[Package.update_content] = update_content
		try:
			Package.query.filter_by(id=pkg_id).update(pkg_update)
			if pkg_file:
				abs_path = os.path.join(config.get("flask", "pkg_path"), pkg_file.filename)
				os.remove(origin_path)
				pkg_file.save(abs_path)
			db.session.commit()
			flash("修改更新包成功")
		except Exception as e:
			app.logger.info("修改更新包(%s)失败" % package.name)
			app.logger.info(str(e))
			db.session.rollback()
			flash("修改更新包失败")
		finally:
			return redirect(url_for("pkg_index"))
	else:
		# 新增
		pkg_file = request.files.get("pkg_file")
		name = pkg_file.filename
		version = request.form.get("version")
		proj_id = request.form.get("proj_id")
		update_level = request.form.get("update_level")
		update_content = request.form.get("update_content")
		package = Package(name, version, proj_id, Package.public_off, update_level, update_content)
		abs_path = os.path.join(config.get("flask", "pkg_path"), name)
		if os.path.exists(abs_path):
			flash("文件名冲突，请修改文件名后再上传，添加更新包失败")
		else:
			pkg_file.save(abs_path)
			try:
				db.session.add(package)
				db.session.commit()
				flash("添加更新包成功")
			except Exception as e:
				app.logger.info("上传更新包失败")
				app.logger.info(str(e))
				os.remove(abs_path)
				db.session.rollback()
				flash("添加更新包失败")
		return redirect(url_for("pkg_index"))


@login_required
def pkg_info():
	pkg_id = request.form.get("pkg_id") or request.args.get("pkg_id")
	if not pkg_id:
		return json.dumps({"status": "error", "err_msg": "缺少参数"})
	else:
		package = Package.query.filter_by(id=pkg_id).first()
		if package is None:
			return josn.dumps({"status": "error", "err_msg": "不存在的proj_id"})
		else:
			return package.to_json()


@login_required
def pkg_public():
	pkg_id = request.args.get("pkg_id")
	public_status = request.args.get("public_status")
	if not pkg_id or not public_status:
		flash("缺少参数")
	else:
		if public_status == str(Package.public_off):
			pub_msg = "取消发布"
		else:
			pub_msg = "发布"
		try:
			Package.query.filter_by(id=pkg_id).update({Package.public_status: public_status})
			db.session.commit()
			flash("%s成功" % pub_msg)
		except Exception as e:
			app.logger.info("%s失败" % pub_msg)
			app.logger.info(str(e))
			db.session.rollback()
			flash("%s失败" % pub_msg)
	return redirect(url_for("pkg_index"))


@login_required
def pkg_delete():
	# 程序包删除
	pkg_id = request.args.get("pkg_id")
	package = Package.query.filter_by(id=pkg_id).first_or_404()
	pkg_name = package.name
	abs_path = os.path.join(config.get("flask", "pkg_path"), pkg_name)
	try:
		os.remove(abs_path)
		db.session.delete(package)
		db.session.commit()
		flash("程序包(%s)删除成功" % pkg_name)
	except Exception as e:
		app.logger.info("程序包删除失败")
		app.logger.info(str(e))
		flash("程序包删除失败")
	finally:
		return redirect(url_for("pkg_index"))


def pkg_download(pkg_name):
	# 获取程序包
	abs_path = os.path.join(config.get("flask", "pkg_path"), pkg_name)
	try:
		return send_file(abs_path)
	except Exception:
		abort(404)