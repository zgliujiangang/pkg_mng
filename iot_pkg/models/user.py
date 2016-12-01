# -*- coding: utf-8 -*-


from datetime import datetime
from iot_pkg._global import db


class User(db.Model):
	
	__tablename__ = "pkg_user"

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(40), unique=True)
	password = db.Column(db.String(100))
	create_time = db.Column(db.DateTime, default=datetime.now)
	update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

	__table_args__ = (
		db.UniqueConstraint("email", name="unique_user_email"),
		)

	def __init__(self, email, password):
		self.email = email
		self.password = password

	# def __str__(self):
	# 	return self.email

	def to_dict(self):
		return {"id": self.id, "email": self.email}