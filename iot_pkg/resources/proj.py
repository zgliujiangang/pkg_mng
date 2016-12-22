# -*- coding: utf-8 -*-


import imghdr
from werkzeug import FileStorage
from flask import send_file
from sqlalchemy.exc import IntegrityError
from flask_restful import request, Resource, reqparse, abort
from flask_restful_swagger import swagger
from iot_pkg import settings
from iot_pkg.core import create_db
from iot_pkg.contrib.auth import login_required
from iot_pkg.contrib.file_storage import File
from iot_pkg.resources.common import page_parser
from iot_pkg.models.proj import Project
from iot_pkg.models.pkg import Package
from iot_pkg.models.counter import DayCounter


db = create_db()


class ProjectListAPI(Resource):

    method_decorators = [login_required]

    get_parser = page_parser.copy()
    get_parser.add_argument("name", type=str, location='args', required=False)
    get_parser.add_argument("platform", type=int, location='args', choices=Project.PLATFORM.keys(), required=False)

    @swagger.operation(
        notes='获取项目列表',
        summary='获取项目列表',
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
                'name': 'name',
                'description': '项目名称',
                'required': False,
                'dataType': 'string',
                'paramType': 'query'
            },
            {
                'name': 'platform',
                'description': '运行平台:(1, Windows)(2, Mac)(3, Android)(4, IOS)',
                'required': False,
                'dataType': 'integer',
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
        projects = request.user.projects.order_by(Project.id.desc())
        if args["name"] is not None:
            projects = projects.filter(Project.name.ilike("%" + args["name"] + "%"))
        if args["platform"] is not None:
            projects = projects.filter_by(platform=args["platform"])
        projects = projects.outerjoin(Package, Project.id==Package.project_id)\
            .with_entities(Project, Package.version_name).group_by(Project.id)
        paginate = projects.paginate(args["page"], per_page=args["per_page"])
        projects = [dict(project.to_dict(), version_name=v) for project, v in paginate.items]
        data = {
            "page": paginate.page, 
            "per_page": paginate.per_page, 
            "pages": paginate.pages,
            "total": paginate.total,
            "projects": projects
        }
        return {"code": "200", "msg": "获取项目列表成功", "data": data}


class ProjectAPI(Resource):

    method_decorators = [login_required]

    get_parser = reqparse.RequestParser()
    get_parser.add_argument("project_id", type=int, required=True)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("name", type=str, required=True)
    post_parser.add_argument("platform", type=int, choices=Project.PLATFORM.keys(), required=True)
    post_parser.add_argument("logo", type=FileStorage, location='files', required=False)
    post_parser.add_argument("is_auto_publish", type=int, choices=Project.IS_AUTO_PUBLISH.keys(), required=False)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("project_id", type=int, required=True)
    put_parser.add_argument("name", type=str, required=False)
    put_parser.add_argument("platform", type=int, choices=Project.PLATFORM.keys(), required=False)
    put_parser.add_argument("logo", type=FileStorage, location='files', required=False)
    put_parser.add_argument("is_auto_publish", type=int, choices=Project.IS_AUTO_PUBLISH.keys(), required=False)

    delete_parser = reqparse.RequestParser()
    delete_parser.add_argument("project_id", type=int, required=True)

    @swagger.operation(
        notes='获取项目信息（需要token）',
        summary='获取项目信息（需要token）',
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
                'required': False,
                'dataType': 'string',
                'paramType': 'query'
            }
        ])
    def get(self):
        args = self.get_parser.parse_args()
        project = Project.query.filter_by(id=args["project_id"], owner=request.user).first_or_404()
        package = project.pkgs.order_by(Package.id.desc()).first()
        if package:
            version_name = package.version_name
        else:
            version_name = None
        data = {"project": dict(project.to_dict(), version_name=version_name)}
        return {"code": "200", "msg": "获取项目信息成功", "data": data}

    @swagger.operation(
        notes='新增项目',
        summary='新增项目',
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
                'name': 'name',
                'description': '项目名称',
                'required': True,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'platform',
                'description': '运行平台:(1, Windows)(2, Mac)(3, Android)(4, IOS)',
                'required': False,
                'dataType': 'integer',
                'paramType': 'form'
            },
            {
                'name': 'logo',
                'description': '项目logo',
                'required': False,
                'dataType': 'file',
                'paramType': 'body'
            },
            {
                'name': 'is_auto_publish',
                'description': '是否自动发布: (0, 手动发布)(1, 自动发布)',
                'required': False,
                'dataType': 'integer',
                'paramType': 'form'
            }
        ])
    def post(self):
        args = self.post_parser.parse_args()
        logo = args["logo"]
        if logo:
            logo_file = File.save(logo)
            logo_id = logo_file.fid
            if imghdr.what(logo_file.save_path) is None:
                logo_file.delete()
                return {'code': '400', 'msg': '上传的图片格式不正确'}
            if logo_file.size >= 500000:
                logo_file.delete()
                return {'code': '400', 'msg': '上传的图片已超过500KB'}
        else:
            logo_id = None
        name = unicode(args['name'])
        project = Project(name, request.user.id, args["platform"], logo_id, args["is_auto_publish"])
        try:
            db.session.add(project)
            db.session.commit()
        except IntegrityError:
            if logo_id:
                File(logo_id).delete()
            return {"code": '400', 'msg': '存在同名项目，新增项目失败'}
        data = {"project": project.to_dict()}
        return {"code": "200", "msg": "创建项目成功", "data": data}

    @swagger.operation(
        notes="修改项目",
        summary='修改项目',
        nickname='put',
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
                'name': 'name',
                'description': '项目名称',
                'required': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'platform',
                'description': '运行平台:(1, Windows)(2, Mac)(3, Android)(4, IOS)',
                'required': False,
                'dataType': 'integer',
                'paramType': 'form'
            },
            {
                'name': 'logo',
                'description': '项目logo',
                'required': False,
                'dataType': 'file',
                'paramType': 'body'
            },
            {
                'name': 'is_auto_publish',
                'description': '是否自动发布: (0, 手动发布)(1, 自动发布)',
                'required': False,
                'dataType': 'integer',
                'paramType': 'form'
            }
        ])
    def put(self):
        args = self.put_parser.parse_args()
        project = Project.query.filter_by(id=args["project_id"], owner=request.user).first_or_404()
        if args["name"] is not None:
            project.name = unicode(args["name"])
        if args["platform"] is not None:
            project.platform = args["platform"]
        if args["logo"] is not None:
            new_logo = File.save(args["logo"])
            if imghdr.what(new_logo.save_path) is None:
                new_logo.delete()
                return {'code': '400', 'msg': '上传的图片格式不正确'}
            if new_logo.size >= 500000:
                new_logo.delete()
                return {'code': '400', 'msg': '上传的图片已超过500KB'}
            if project.logo:
                File(project.logo).delete()
            project.logo = new_logo.fid
        if args["is_auto_publish"] is not None:
            project.is_auto_publish = args["is_auto_publish"]
        try:
            db.session.commit()
        except IntegrityError:
            if args['logo'] is not None:
                File(project.logo).delete()
            return {"code": '400', 'msg': '存在同名项目，修改项目失败'}
        data = {"project": project.to_dict()}
        return {"code": "200", "msg": "项目修改成功", "data": data}

    @swagger.operation(
        notes='删除项目',
        summary='删除项目',
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
                'name': 'project_id',
                'description': '项目ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'form'
            }
        ])
    def delete(self):
        args = self.delete_parser.parse_args()
        # 1、删除logo 2、删除package及其dependents记录 3、删除project本身
        project = Project.query.filter_by(id=args["project_id"], owner=request.user).first_or_404()
        if project.logo:
            logo = File(project.logo)
            logo.delete()
        for pkg in project.pkgs:
            pkg.dependents.delete()
            db.session.delete(pkg)
        db.session.delete(project)
        db.session.commit()
        return {"code": "200", "msg": "删除项目成功"}


class ProjectMsgAPI(Resource):

    @swagger.operation(
        notes='获取项目信息（无需token）',
        summary='获取项目信息（无需token）',
        nickname='get',
        parameters=[
            {
                'name': 'uid',
                'description': '给项目随机分配的uid',
                'required': True,
                'dataType': 'string',
                'paramType': 'path'
            }
        ])
    def get(self, uid):
        project = Project.query.filter_by(uid=uid).first_or_404()
        data = {"project": project.to_dict()}
        return {"code": "200", "msg": "获取项目信息成功", "data": data}


class ProjectFileAPI(Resource):

    def get(self, uid):
        project = Project.query.filter_by(uid=uid).first_or_404()
        packages = project.pkgs.order_by(Package.version_name.desc())
        latest_package = None
        for pkg in packages:
            dpt_pkgs = pkg.dependents
            all_exists = True
            for dpt in dpt_pkgs:
                dpt_exists = Package.query.filter_by(project_id=dpt.project_id, version_name=dpt.version_name).scalar()
                if not dpt_exists:
                    all_exists = False
                    break
            if all_exists:
                latest_package = pkg
            else:
                continue
        if latest_package:
            package_file = File(latest_package.fid)
            counter = DayCounter.get_counter(project.uid)
            counter.increase()
            return send_file(package_file.file, as_attachment=True, attachment_filename=package_file.filename)
        else:
            abort(404)