# -*- coding: utf-8 -*-


from datetime import datetime
from flask import url_for
from iot_pkg.contrib.file_storage import File
from iot_pkg.core import create_db
from iot_pkg import settings


db = create_db()


class Package(db.Model):

    __tablename__ = "pkg_package"

    public_off = 0
    public_on = 1
    PUBLIC_STATUS = {public_off: "未发布", public_on: "已发布"}

    update_free = 0
    update_must = 1
    UPDATE_LEVEL = {update_free: "非强制更新", update_must: "强制更新"}

    id = db.Column(db.Integer, primary_key=True)
    version_name = db.Column(db.String(20), nullable=False)
    build_code = db.Column(db.String(20), nullable=False)
    fid = db.Column(db.String(50), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("pkg_project.id"), nullable=False)
    project = db.relationship("Project", backref=db.backref("pkgs", lazy="dynamic"))
    channel = db.Column(db.String(20), default='')
    public_status = db.Column(db.Integer, default=public_off)
    update_level = db.Column(db.Integer, default=update_free)
    update_content = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        # 相同项目一个版本只能有一条记录
        db.UniqueConstraint("project_id", "build_code", 'channel', name="unique_proj_build_channel"),
        )

    def __init__(self, version_name=None, build_code=None, fid=None, project_id=None,
                 public_status=None, update_level=None, update_content=None, channel=None):
        self.version_name = version_name
        self.build_code = build_code
        self.fid = fid
        self.project_id = project_id
        self.public_status = public_status
        self.update_level = update_level
        self.update_content = update_content
        self.channel = channel

    def __str__(self):
        return self.file.filename

    @property
    def file(self):
        return File(self.fid)

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['version_name'] = self.version_name
        data['build_code'] = int(self.build_code)
        data['fid'] = self.fid
        data['public_status'] = self.public_status
        data['public_status_display'] = self.PUBLIC_STATUS.get(self.public_status)
        data['update_level'] = self.update_level
        data['update_level_display'] = self.UPDATE_LEVEL.get(self.update_level)
        data['update_content'] = self.update_content
        data["download_url"] = settings.DOMAIN + url_for('package_download', fid=self.fid)
        pkg_file = File(self.fid)
        data['filename'] = pkg_file.filename
        data['filesize'] = pkg_file.size
        data['dependents'] = [dpt.to_dict() for dpt in self.dependents.all()]
        data['create_time'] = self.create_time.strftime('%Y-%m-%d %H:%M')
        data['channel'] = self.channel
        return data


class PackageDependent(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey("pkg_package.id"), nullable=False)
    package = db.relationship("Package", backref=db.backref("dependents", lazy="dynamic"))
    project_id = db.Column(db.Integer, db.ForeignKey("pkg_project.id"), nullable=False)
    project = db.relationship("Project")
    version_name = db.Column(db.String(20), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, package_id, project_id, version_name):
        self.package_id = package_id
        self.project_id = project_id
        self.version_name = version_name

    def to_dict(self):
        return {'project_id': self.project_id, 'version_name': self.version_name}