# /usr/bin/env python
# -*- coding: utf-8 -*-


from datetime import datetime
from _global import db


class Project(db.Model):

	__tablename__ = "pkg_project"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), index=True, unique=True, nullable=False)
	create_time = db.Column(db.DateTime, default=datetime.now)
	update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
	
	def __init__(self, name):
		self.name = name

	def __str__(self):
		return self.name