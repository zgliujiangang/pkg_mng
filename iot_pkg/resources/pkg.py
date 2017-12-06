# -*- coding:utf-8 -*-
import json
import re
import mimetypes
from werkzeug import FileStorage
from sqlalchemy.exc import IntegrityError
from flask import send_file, Response
from flask_restful import request, reqparse, Resource, abort
from flask_restful_swagger import swagger

from iot_pkg import settings
from iot_pkg.core import create_db
from iot_pkg.contrib.auth import login_required
from iot_pkg.contrib.file_storage import File, get_partial_file
from iot_pkg.contrib.pkg_parser import pkg_parser
from iot_pkg.resources.common import page_parser
from iot_pkg.models.proj import Project
from iot_pkg.models.counter import DayCounter
from iot_pkg.models.pkg import Package, PackageDependent
from iot_pkg.models.channel import Channel

db = create_db()


class PackageListAPI(Resource):

    method_decorators = [login_required]

    get_parser = page_parser.copy()
    get_parser.add_argument("project_id", type=int, required=True)
    get_parser.add_argument('channel', type=str, required=False)

    @swagger.operation(
        notes='获取安装包列表',
        summary='获取安装包列表',
        nickname='get',
        parameters=[
            {
                "name": settings.USER_SESSION_KEY,
                "description": "登录凭证",
                'required': True,
                'dataType': 'string',
                'paramType': 'header'
            },
            {
                'name': 'project_id',
                'description': '项目ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'query'
            },
            {
                'name': 'channel',
                'description': '渠道名称',
                'required': False,
                'dataType': 'string',
                'paramType': 'query'
            },
            {
                'name': 'page',
                'description': '页数',
                'required': False,
                'dataType': 'integer',
                'paramType': 'query'
            },
            {
                'name': 'per_page',
                'description': '每页条数',
                'required': False,
                'dataType': 'integer',
                'paramType': 'query'
            }
        ])
    def get(self):
        args = self.get_parser.parse_args()
        project_id = args["project_id"]
        channel = unicode(args['channel']) if args['channel'] else ''
        project = Project.query.filter_by(id=project_id, owner=request.user).first_or_404()
        packages = project.pkgs.order_by(Package.build_code.desc())
        project_data = project.to_dict(channel=channel)
        packages = packages.filter_by(channel=channel)
        project_data["today_download"] = DayCounter.get_counter(cid=project.uid).number
        project_data["total_download"] = DayCounter.get_counters(cid=project.uid).with_entities(db.func.sum(DayCounter.number)).one()[0]
        paginate = packages.paginate(args["page"], per_page=args["per_page"])
        data = {
            "page": paginate.page, 
            "per_page": paginate.per_page, 
            "pages": paginate.pages,
            "total": paginate.total,
            "project": project_data, 
            "packages": [package.to_dict() for package in paginate.items]
        }
        return {"code": "200", "msg": "获取安装包列表成功", "data": data}


class PackageAPI(Resource):

    method_decorators = [login_required]

    get_parser = reqparse.RequestParser()
    get_parser.add_argument("package_id", type=int, required=True)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("project_id", type=int, required=True)
    post_parser.add_argument("fid", required=True)
    post_parser.add_argument("version_name", required=True)
    post_parser.add_argument("build_code", required=True, type=int)
    post_parser.add_argument("update_level", required=False)
    post_parser.add_argument("update_content", required=False)
    post_parser.add_argument("dependent_pkgs", required=False)
    post_parser.add_argument('channel', required=False)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("package_id", type=int, required=True)
    put_parser.add_argument("fid", required=False)
    put_parser.add_argument("version_name", required=False)
    put_parser.add_argument("build_code", required=False, type=int)
    put_parser.add_argument("update_level", required=False)
    put_parser.add_argument("update_content", required=False, default="")
    put_parser.add_argument("dependent_pkgs", required=False)
    put_parser.add_argument("public_status", required=False)
    put_parser.add_argument('channel', required=False)

    delete_parser = reqparse.RequestParser()
    delete_parser.add_argument("package_id", type=int, required=True)

    @swagger.operation(
        notes='获取安装包信息',
        summary='获取安装包信息',
        nickname='get',
        parameters=[
            {
                "name": settings.USER_SESSION_KEY,
                "description": "登录凭证",
                'required': True,
                'dataType': 'string',
                'paramType': 'header'
            },
            {
                'name': 'package_id',
                'description': '安装包ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'query'
            }
        ])
    def get(self):
        args = self.get_parser.parse_args()
        package_id = args["package_id"]
        package = Package.query.filter_by(id=package_id).join(Project, Package.project_id==Project.id).filter(Project.owner==request.user).first_or_404()
        data = {"package": package.to_dict()}
        return {"code": "200", "msg": "获取安装包信息成功", "data": data}

    @swagger.operation(
        notes='上传安装包',
        summary='上传安装包',
        nickname='post',
        parameters=[
            {
                "name": settings.USER_SESSION_KEY,
                "description": "登录凭证",
                'required': True,
                'dataType': 'string',
                'paramType': 'header'
            },
            {
                'name': 'project_id',
                'description': '项目ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'form'
            },
            {
                'name': 'version_name',
                'description': '版本名称',
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'build_code',
                'description': 'build号',
                'required': True,
                'dataType': 'int',
                'paramType': 'form'
            },
            {
                'name': 'fid',
                'description': '上传安装包文件后获取的文件FID',
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'update_level',
                'description': '是否强制更新',
                'required': False,
                'dataType': 'integer',
                'paramType': 'form'
            },
            {
                'name': 'update_content',
                'description': '更新内容',
                'required': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'dependent_pkgs',
                'description': '依赖的安装包列表',
                'required': False,
                'dataType': 'json',
                'paramType': 'form'
            },
            {
                'name': 'channel',
                'description': '渠道名称',
                'required': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        args = self.post_parser.parse_args()
        channel = unicode(args['channel']) if args['channel'] else ''
        project = Project.query.filter_by(id=args["project_id"], owner=request.user).first_or_404()
        package = Package()
        package.version_name = args["version_name"]
        package.build_code = args["build_code"]
        package.fid = args["fid"]
        package.project_id = args["project_id"]
        package.update_level = args["update_level"]
        package.update_content = args["update_content"]
        package.channel = channel
        if channel and not Channel.query.filter_by(project_id=args['project_id'], name=channel).first():
            channel = Channel(channel, args['project_id'])
            db.session.add(channel)
            db.session.commit()
        if project.is_auto_publish == Project.AUTO_PUBLISH:
            package.public_status = Package.public_on
        else:
            package.public_status = Package.public_off
        try:
            db.session.add(package)
            db.session.commit()
        except IntegrityError:
            return {'code': '400', 'msg': '该项目下已存在相同build号和渠道的安装包'}
        try:
            dependent_pkgs = json.loads(args["dependent_pkgs"])
            for pkg in dependent_pkgs:
                dependent_pkg = PackageDependent(package.id, pkg["project_id"], pkg["version_name"])
                db.session.add(dependent_pkg)
                db.session.commit()
        except Exception as e:
            print e
        data = {"package": package.to_dict()}
        return {"code": "200", "msg": "添加安装包成功", "data": data}

    @swagger.operation(
        notes='修改安装包',
        summary='修改安装包',
        nickname='post',
        parameters=[
            {
                "name": settings.USER_SESSION_KEY,
                "description": "登录凭证",
                'required': True,
                'dataType': 'string',
                'paramType': 'header'
            },
            {
                'name': 'package_id',
                'description': '安装包ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'form'
            },
            {
                'name': 'version_name',
                'description': '版本名称',
                'required': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'build_code',
                'description': 'build号',
                'required': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'fid',
                'description': '上传安装包文件后获取的文件FID',
                'required': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'update_level',
                'description': '是否强制更新',
                'required': False,
                'dataType': 'integer',
                'paramType': 'form'
            },
            {
                'name': 'update_content',
                'description': '更新内容',
                'required': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'dependent_pkgs',
                'description': '依赖的安装包列表',
                'required': False,
                'dataType': 'json',
                'paramType': 'form'
            },
            {
                'name': 'public_status',
                'description': '是否发布, (0, 未发布)(1, 已发布)',
                'required': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'channel',
                'description': '渠道名称',
                'required': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def put(self):
        args = self.put_parser.parse_args()
        package_id = args["package_id"]
        package = Package.query.filter_by(id=package_id).join(Project, Package.project_id==Project.id).filter(Project.owner==request.user).first_or_404()
        channel = unicode(args['channel']) if args['channel'] else ''
        if args["version_name"]:
            package.version_name = args["version_name"]
        if args["build_code"]:
            package.build_code = args["build_code"]
        if args["fid"] and args["fid"] != package.fid:
            File(package.fid).delete()
            package.fid = args["fid"]
        if args["update_level"]:
            package.update_level = args["update_level"]
        if channel:
            package.channel = channel
            if not Channel.query.filter_by(project_id=package.project_id, name=channel).first():
                channel = Channel(channel, package.project_id)
                db.session.add(channel)
                db.session.commit()
        if args["public_status"]:
            # 这段代码你可能看不懂，但是就应该这么写
            package.public_status = args["public_status"]
        else:
            package.update_content = args["update_content"]
        if args["dependent_pkgs"]:
            try:
                # dpt_pkgs = package.dependents
                # db.session.delete(dpt_pkgs)
                package.dependents.delete()
                dependent_pkgs = json.loads(args["dependent_pkgs"])
                for pkg in dependent_pkgs:
                    dependent_pkg = PackageDependent(package.id, pkg["project_id"], pkg["version_name"])
                    db.session.add(dependent_pkg)
                    db.session.commit()
            except Exception as e:
                print e
        try:
            db.session.commit()
        except IntegrityError:
            return {'code': '400', 'msg': '该项目下已存在相同build号和渠道的安装包'}
        data = {"package": package.to_dict()}
        return {"code": "200", "msg": "修改安装包信息成功", "data": data}

    @swagger.operation(
        notes='删除安装包',
        summary='删除安装包',
        nickname='delete',
        parameters=[
            {
                "name": settings.USER_SESSION_KEY,
                "description": "登录凭证",
                'required': True,
                'dataType': 'string',
                'paramType': 'header'
            },
            {
                'name': 'package_id',
                'description': '安装包ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'form'
            }
        ])
    def delete(self):
        args = self.delete_parser.parse_args()
        package_id = args["package_id"]
        package = Package.query.filter_by(id=package_id).join(Project, Package.project_id==Project.id).filter(Project.owner==request.user).first_or_404()
        # dpt_pkgs = package.dependents.delete()
        # db.session.delete(dpt_pkgs)
        package.dependents.delete()
        File(package.fid).delete()
        db.session.delete(package)
        db.session.commit()
        return {"code": "200", "msg": "删除安装包成功"}


class PackageFileAPI(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('range', location='headers')

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("project_id", type=int, required=True)
    post_parser.add_argument("package", type=FileStorage, location='files', required=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("package_id", type=int, required=True)
    put_parser.add_argument("package", type=FileStorage, location='files', required=True)

    def get(self, fid):
        package = Package.query.filter_by(fid=fid).first_or_404()
        project = package.project
        counter = DayCounter.get_counter(project.uid)
        counter.increase()
        req_file = File(fid)
        args = self.get_parser.parse_args()
        if args['range']:
            range_match = re.search('^bytes=(\d+)-(\d*)$', args['range'])
            range_match = range_match.groups()
            start_byte = range_match[0]
            if start_byte:
                start_byte = int(start_byte)
            end_byte = range_match[1]
            if end_byte:
                end_byte = int(end_byte)
            else:
                end_byte = req_file.size
            file_data = get_partial_file(req_file, start_byte, end_byte)
            resp = Response(file_data,
                            206,
                            mimetype=mimetypes.guess_type(req_file.save_path)[0],
                            direct_passthrough=True)
            content_range = 'bytes {start}-{end}/{size}'.format(start=start_byte,
                                                                end=end_byte,
                                                                size=req_file.size)
            resp.headers.add('Content-Range', content_range)
            return resp
        else:
            try:
                return send_file(req_file.save_path, as_attachment=True, attachment_filename=req_file.filename)
            except IOError:
                abort(404)
            except Exception as e:
                print str(e)
                abort(400)

    @swagger.operation(
        notes='上传安装包文件',
        summary='上传安装包文件',
        nickname='post',
        parameters=[
            {
                "name": settings.USER_SESSION_KEY,
                "description": "登录凭证",
                'required': True,
                'dataType': 'string',
                'paramType': 'header'
            },
            {
                'name': 'project_id',
                'description': '项目ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'form'
            },
            {
                'name': 'package',
                'description': '安装包文件',
                'required': True,
                'dataType': 'file',
                'paramType': 'body'
            }
        ])
    @login_required
    def post(self):
        args = self.post_parser.parse_args()
        package = File.save(args["package"])
        pkg_info = pkg_parser.start_parse(package)
        data = {
            "project_id": args["project_id"],
            "fid": package.fid,
            "filename": package.filename,
            "info": pkg_info
        }
        return {"code": "200", "msg": "解析安装包文件成功", "data": data} 

    @swagger.operation(
        notes='重新上传安装包文件',
        summary='重新上传安装包文件',
        nickname='post',
        parameters=[
            {
                "name": settings.USER_SESSION_KEY,
                "description": "登录凭证",
                'required': True,
                'dataType': 'string',
                'paramType': 'header'
            },
            {
                'name': 'package_id',
                'description': '安装包ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'form'
            },
            {
                'name': 'package',
                'description': '安装包文件',
                'required': True,
                'dataType': 'file',
                'paramType': 'body'
            }
        ])
    @login_required
    def put(self):
        args = self.put_parser.parse_args()
        package = File.save(args["package"])
        pkg_info = pkg_parser.start_parse(package)
        data = {
            "package_id": args["package_id"],
            "fid": package.fid,
            "filename": package.filename,
            "info": pkg_info
        }
        return {"code": "200", "msg": "解析安装包文件成功", "data": data}