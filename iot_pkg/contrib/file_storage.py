# -*- coding: utf-8 -*-


import os
import uuid
from iot_pkg import settings
from iot_pkg.core import create_api, create_cache


api = create_api()
cache = create_cache()


class File(object):

    def __init__(self, fid):
        self.fid = fid

    @classmethod
    def save(cls, _file):
        # _file is a instance of werkzeug.FileStorage
        file_id = str(uuid.uuid4())
        save_file = cls(file_id)
        save_file.file = _file
        save_file.filename = _file.filename
        return save_file

    def delete(self):
        # delete the file
        self.file = None
        self.filename = None
        return True

    @property
    def save_path(self):
        return os.path.join(settings.FILE_PATH, self.fid)

    @property
    def file(self):
        _fp = open(self.save_path, "rb")
        return _fp

    @file.setter
    def file(self, _file):
        save_path = self.save_path
        if _file is None:
            os.remove(save_path)
        else:
            _file.save(save_path)

    @property
    def filename(self):
        return cache.get(self.fid)

    @filename.setter
    def filename(self, value):
        if value is None:
            cache.delete(self.fid)
        else:
            cache.set(self.fid, value)

    @property
    def size(self):
        return os.path.getsize(self.save_path)