# -*- coding: utf-8 -*-


import uuid
from datetime import date
from iot_pkg.core import create_db


db = create_db()


class DayCounter(db.Model):

    __tablename__ = "pkg_day_counter"

    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.String(50), default=lambda:str(uuid.uuid4()), nullable=False)
    create_date = db.Column(db.Date, default=date.today)
    number = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, cid=None, create_date=None):
        self.cid = cid
        self.create_date = create_date

    def increase(self, number=1):
        self.number += number
        db.session.commit()

    @classmethod
    def get_counter(cls, cid=None, create_date=None):
        if not create_date:
            create_date = date.today()
        counter = cls.query.filter_by(cid=cid, create_date=create_date).first()
        if not counter:
            counter = cls(cid, create_date)
            db.session.add(counter)
            db.session.commit()
        return counter

    @classmethod
    def get_counters(cls, cid):
        return cls.query.filter_by(cid=cid)