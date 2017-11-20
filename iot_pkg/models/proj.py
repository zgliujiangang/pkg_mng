# -*- coding: utf-8 -*-


import uuid
from flask import url_for
from datetime import datetime, date
try:
    from werkzeug.urls import url_unquote
except ImportError:
    from urlparse import quote as url_unquote
from iot_pkg import settings
from iot_pkg.core import create_db
from iot_pkg.models.counter import DayCounter
from iot_pkg.utils import get_random_string


db = create_db()


class Project(db.Model):

    __tablename__ = "pkg_project"

    Windows = 1
    Mac = 2
    Android = 3
    IOS = 4
    PLATFORM = {Windows: "Windows", Mac: "Mac", Android: "Android", IOS: "IOS"}

    NOT_AUTO_PUBLISH = 0
    AUTO_PUBLISH = 1
    IS_AUTO_PUBLISH = {AUTO_PUBLISH: "自动发布", NOT_AUTO_PUBLISH: "手动发布"}

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True, default=lambda:str(uuid.uuid4()), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("pkg_user.id"), nullable=False)
    owner = db.relationship("User", backref=db.backref("projects", lazy="dynamic"))
    platform = db.Column(db.Integer, nullable=True)
    logo = db.Column(db.String(50), nullable=True)
    is_auto_publish = db.Column(db.Integer, nullable=False, default=AUTO_PUBLISH)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        # 相同项目一个版本只能有一条记录
        db.UniqueConstraint("owner_id", "name", name="unique_user_project"),
        )

    def __init__(self, name, owner_id, platform, logo, is_auto_publish):
        self.name = name
        self.owner_id = owner_id
        self.platform = platform
        self.logo = logo
        self.is_auto_publish = is_auto_publish
        self.uid = self.make_uid()

    def __str__(self):
        return self.name

    def make_uid(self):
        return unicode(str(self.name) + '_' + get_random_string(3))

    def to_dict(self, channel=None):
        if channel:
            msg_url = settings.DOMAIN + url_unquote(url_for("project_msg", uid=self.uid, channel=channel))
            download_url = settings.DOMAIN + url_unquote(url_for("project_download", uid=self.uid, channel=channel))
        else:
            msg_url = settings.DOMAIN + url_unquote(url_for("project_msg", uid=self.uid))
            download_url = settings.DOMAIN + url_unquote(url_for("project_download", uid=self.uid))
        data = {
            "id": self.id,
            "uid": self.uid,
            "name": self.name,
            "platform": self.platform,
            "platform_display": self.PLATFORM.get(self.platform),
            "logo": self.logo,
            "auto_publish": self.is_auto_publish,
            "auto_publish_display": self.IS_AUTO_PUBLISH.get(self.is_auto_publish),
            "msg_url": msg_url,
            "download_url": download_url
        }
        # data["today_download"] = DayCounter.get_counter(self.uid).number
        # data["total_download"] = DayCounter.get_counters(cid=self.uid).with_entities(db.func.sum(DayCounter.number)).one()[0]
        return data