# /usr/bin/env python
# -*- coding: utf-8 -*-


import json
from datetime import datetime
from _global import db
from flask import url_for


class Package(db.Model):

	__tablename__ = "pkg_package"

	public_off = 1
	public_on = 2
	PUBLIC_STATUS = {public_off: "未发布", public_on: "已发布"}	# 发布状态

	update_free = 1
	update_must = 2
	UPDATE_LEVEL = {update_free: "否", update_must: "是"}	# 是否强制更新

	Windows = 1
	Mac = 2
	Android = 3
	IOS = 4
	PLATFORM = {Windows: "Windows", Mac: "Mac", Android: "Android", IOS: "IOS"}

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), nullable=False, unique=True)
	version_name = db.Column(db.String(20), nullable=False)
	version_code = db.Column(db.Integer, index=True)
	project_id = db.Column(db.Integer, db.ForeignKey("pkg_project.id"), nullable=False)
	project = db.relationship("Project", backref=db.backref("pkgs", lazy="dynamic"))
	platform = db.Column(db.Integer, nullable=True)
	public_status = db.Column(db.Integer, default=public_off)
	update_level = db.Column(db.Integer, default=update_free)
	update_content = db.Column(db.Text)
	create_time = db.Column(db.DateTime, default=datetime.now)
	update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	
	__table_args__ = (
		# 相同项目一个版本只能有一条记录
		db.UniqueConstraint("project_id", "version_code", name="unique_proj_version"),
		)
	
	def __init__(self, name, version_name, version_code, project_id, public_status=public_off, update_level=update_free, update_content=None):
		self.name = name
		self.version_name = version_name
		self.version_code = version_code
		self.project_id = project_id
		self.public_status = public_status
		self.update_level=update_level
		self.update_content = update_content

	def __str__(self):
		return self.project.name + self.version_name

	def to_json(self):
		data = {"name": self.name, "version_name": self.version_name, "version_code": self.version_code, "proj_name": self.project.name, 
		"proj_id": self.project_id, "public_status": self.public_status, "update_level": 
		self.update_level, "update_content": self.update_content, "id": self.id, 
		"download_url": url_for("pkg_download", pkg_name=self.name, _external=True)}
		return json.dumps(data)


