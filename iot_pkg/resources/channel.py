# -*- coding: utf-8 -*-
from flask_restful_swagger import swagger

from iot_pkg.resources.common import page_parser
from flask_restful import Resource, reqparse
from iot_pkg.contrib.auth import login_required
from iot_pkg import settings
from iot_pkg.models.channel import Channel
from iot_pkg.core import create_db

db = create_db()


class ChannleListAPI(Resource):
    method_decorators = [login_required]

    get_parser = page_parser.copy()
    get_parser.add_argument("project_id", type=int, required=True)

    @swagger.operation(
        notes='获取项目渠道列表',
        summary='获取项目渠道列表',
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
        channels = Channel.query.filter_by(project_id=project_id)
        paginate = channels.paginate(args["page"], per_page=args["per_page"])
        channels = [channel.to_dict() for channel in paginate.items]
        data = {
            "page": paginate.page,
            "per_page": paginate.per_page,
            "pages": paginate.pages,
            "total": paginate.total,
            "channels": channels
        }
        return {"code": "200", "msg": "获取项目渠道列表成功", "data": data}


class ChannelAPI(Resource):
    method_decorators = [login_required]

    get_parser = reqparse.RequestParser()
    get_parser.add_argument("channel_id", type=int, required=True)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("name", type=str, required=True)
    post_parser.add_argument("project_id", type=int, required=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("channel_id", type=int, required=True)
    post_parser.add_argument("name", type=str, required=True)

    delete_parser = reqparse.RequestParser()
    delete_parser.add_argument("channel_id", type=int, required=True)

    @swagger.operation(
        notes='获取项目渠道详情',
        summary='获取项目渠道详情',
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
                'name': 'channel_id',
                'description': '渠道ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'query'
            }
        ])
    def get(self):
        args = self.get_parser.parse_args()
        channel_id = args['channel_id']
        channel = Channel.query.filter_by(id=channel_id).first_or_404()
        data = {"channel": channel.to_dict()}
        return {"code": "200", "msg": "获取项目信息成功", "data": data}

    @swagger.operation(
        notes='新增项目渠道',
        summary='新增项目渠道',
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
                'name': 'name',
                'description': '渠道名称',
                'required': True,
                'dataType': 'string',
                'paramType': 'form',
            }
        ])
    def post(self):
        args = self.post_parser.parse_args()
        project_id = args['project_id']
        channel_name = unicode(args["name"])
        channel = Channel.query.filter_by(project_id=project_id, name=channel_name).first()
        if channel:
            return {"code": '400', 'msg': '同一项目存在同名渠道，新增项目渠道失败'}
        else:
            channel = Channel(channel_name, project_id)
            db.session.add(channel)
            db.session.commit()
            return {"code": "200", "msg": "创建项目渠道成功", "data": channel.to_dict()}

    @swagger.operation(
        notes='新增项目渠道',
        summary='新增项目渠道',
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
                'name': 'channel_id',
                'description': '项目渠道ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'form'
            },
            {
                'name': 'name',
                'description': '渠道名称',
                'required': True,
                'dataType': 'string',
                'paramType': 'form',
            }
        ])
    def put(self):
        args = self.put_parser.parse_args()
        channel_id = args['channel_id']
        channel_name = unicode(args["name"])
        channel = Channel.query.filter_by(id=channel_id).first_or_404()
        if Channel.query.filter_by(project_id=channel.project_id, name=channel_name).first():
            return {"code": '400', 'msg': '同一项目存在同名渠道，修改项目渠道失败'}
        else:
            channel.name = channel_name
            db.session.add(channel)
            db.session.commit()
            return {"code": "200", "msg": "修改项目渠道成功", "data": channel.to_dict()}

    @swagger.operation(
        notes='删除项目渠道',
        summary='删除项目渠道',
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
                'name': 'channel_id',
                'description': '项目渠道ID',
                'required': True,
                'dataType': 'integer',
                'paramType': 'form'
            }
        ])
    def delete(self):
        args = self.delete_parser.parse_args()
        channel_id = args['channel_id']
        channel = Channel.query.filter_by(id=channel_id).first_or_404()
        db.session.delete(channel)
        db.session.commit()
        return {"code": "200", "msg": "删除项目渠道成功"}
