# /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
from flask import request
from flask import send_file
from flask import render_template
from flask import redirect
from flask import flash
from flask import url_for
from flask import make_response
from models.proj import Project
from models.pkg import Package
from _global import db, app, config
from common import login_required


@login_required
def proj_index():
	# 项目列表
	proj_query = Project.query.order_by(Project.id.desc())
	page = request.args.get("page") or 1
	per_page = request.args.get("per_page") or 20
	try:
		page, per_page = int(page), int(per_page)
	except ValueError:
		page, per_page = 1, 20
	limit = per_page
	offset = (page - 1) * per_page
	if request.args.get("name"):
		proj_query = proj_query.filter(Project.name.ilike("%" + request.args.get("name") + "%"))
	if request.args.get("proj_id"):
		proj_query = proj_query.filter_by(id=request.args.get("proj_id"))
	proj_list = proj_query.offset(offset).limit(limit).all()
	proj_count = proj_query.count()
	page_count = proj_count / per_page + 1 if proj_count % per_page else proj_count / per_page
	return render_template("proj_list.html", proj_list=proj_list, page_count=page_count, page=page)


@login_required
def proj_add():
	# 项目增改
	proj_id = request.form.get("proj_id") or request.args.get("proj_id")
	name = request.form.get("proj_name") or request.args.get("proj_name")
	if not name:
		flash("缺少参数name")
		return redirect(url_for("proj_index"))
	if proj_id:
		try:
			Project.query.filter_by(id=proj_id).update({Project.name: name})
			db.session.commit()
			flash("修改成功")
		except Exception as e:
			app.logger.info("修改project失败")
			app.logger.info(str(e))
			flash("修改失败")
		finally:
			return redirect(url_for("proj_index"))
	else:
		project = Project(name)
		try:
			db.session.add(project)
			db.session.commit()
			flash("添加成功")
		except Exception as e:
			app.logger.info("添加project失败")
			app.logger.info(str(e))
			flash("添加失败")
		finally:
			return redirect(url_for("proj_index"))


@login_required
def proj_delete():
	proj_id = request.args.get("proj_id")
	project = Project.query.filter_by(id=proj_id).first_or_404()
	try:
		db.session.delete(project)
		db.session.commit()
		flash("删除成功")
	except Exception as e:
		app.logger.info("删除project失败")
		app.logger.info(str(e))
		db.session.rollback()
		flash("删除失败")
	finally:
		return redirect(url_for("proj_index"))


def proj_latest_msg(proj_name):
	project = Project.query.filter_by(name=proj_name).first_or_404()
	pkg = project.pkgs.filter_by(public_status=Package.public_on).order_by(Package.version.desc()).first_or_404()
	return pkg.to_json()


def proj_latest_download(proj_name):
	project = Project.query.filter_by(name=proj_name).first_or_404()
	pkg = project.pkgs.filter_by(public_status=Package.public_on).order_by(Package.version.desc()).first_or_404()
	pkg_name = pkg.name
	abs_path = os.path.join(config.get("flask", "pkg_path"), pkg_name)
	try:
		response = make_response(send_file(abs_path))
		response.headers["Content-Disposition"] = "attachment; filename=%s;" % pkg_name
		return response
	except Exception:
		abort(404)