# -*- coding: utf-8 -*-


from flask_restful import reqparse
from iot_pkg import settings


page_parser = reqparse.RequestParser()
page_parser.add_argument("page", type=int, location='args', required=False, default=settings.DEFAULT_PAGE)
page_parser.add_argument("per_page", type=int, location='args', required=False, default=settings.PER_PAGE)