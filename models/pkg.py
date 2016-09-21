# /usr/bin/env python
# -*- coding: utf-8 -*-


import json
from datetime import datetime
from _global import db


class Package(db.Model):

	__tablename__ = "pkg_package"

	public_off = 1
	public_on = 2
	PUBLIC_STATUS = {public_off: "未发布", public_on: "已发布"}	# 发布状态

	update_free = 1
	update_must = 2
	UPDATE_LEVEL = {update_free: "否", update_must: "是"}	# 是否强制更新

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), nullable=False, unique=True)
	version = db.Column(db.String(20), nullable=False)
	project_id = db.Column(db.Integer, db.ForeignKey("pkg_project.id"), nullable=False)
	project = db.relationship("Project", backref=db.backref("pkgs", lazy="dynamic"))
	public_status = db.Column(db.Integer, default=public_off)
	update_level = db.Column(db.Integer, default=update_free)
	update_content = db.Column(db.Text)
	create_time = db.Column(db.DateTime, default=datetime.now)
	update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	
	__table_args__ = (
		# 相同项目一个版本只能有一条记录
		db.UniqueConstraint("project_id", "version", name="unique_proj_version"),
		)
	
	def __init__(self, name, version, project_id, public_status=public_off, update_level=update_free, update_content=None):
		self.name = name
		self.version = version
		self.project_id = project_id
		self.public_status = public_status
		self.update_level=update_level
		self.update_content = update_content

	def __str__(self):
		return self.project.name + self.version

	def to_json(self):
		data = {"name": self.name, "version": self.version, "proj_name": self.project.name, 
		"proj_id": self.project_id, "public_status": self.public_status, "update_level": 
		self.update_level, "update_content": self.update_content, "id": self.id}
		return json.dumps(data)


