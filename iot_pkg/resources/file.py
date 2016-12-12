# -*- coding: utf-8 -*-


from flask import send_file
from werkzeug import FileStorage
from flask_restful import request, Resource, reqparse, abort
from iot_pkg.contrib.file_storage import File


class FileAPI(Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("file", type=FileStorage, location='files', required=True)

    def get(self, file_id):
        req_file = File(file_id)
        try:
            return send_file(req_file.file, as_attachment=True, attachment_filename=req_file.filename)
        except IOError:
            abort(404)
        except Exception as e:
            print str(e)
            abort(400)

    def post(self):
        args = self.post_parser.parse_args()
        _file = args["file"]
        _file = File.save(_file)
        data = {"file_id": _file.id, "url": _file.url, "filename": _file.filename}
        return {"code": "200", "msg": "上传文件成功", "data": data}