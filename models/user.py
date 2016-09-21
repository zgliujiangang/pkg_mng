# /usr/bin/env python
# -*- coding: utf-8 -*-


from datetime import datetime
from _global import db


class User(db.Model):
	
	__tablename__ = "pkg_user"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), unique=True)
	password = db.Column(db.String(100))
	create_time = db.Column(db.DateTime, default=datetime.now)
	update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

	def __init__(self, name, password):
		self.name = name
		self.password = password

	def __str__(self):
		return self.name