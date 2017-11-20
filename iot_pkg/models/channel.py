# -*- coding: utf-8 -*-
from datetime import datetime
from iot_pkg.core import create_db

db = create_db()


class Channel(db.Model):

    __tablename__ = 'pkg_channel'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("pkg_project.id"), nullable=False)
    project = db.relationship("Project", backref=db.backref("channels", lazy="dynamic"))
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, name, project_id):
        self.name = name
        self.project_id = project_id

    def to_dict(self):
        data = {'id': self.id,
                'project_id': self.project_id,
                'name': self.name}
        return data
