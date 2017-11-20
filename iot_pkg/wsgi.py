# -*- coding: utf-8 -*-


import sys

reload(sys)
sys.path.append("..")
sys.setdefaultencoding('utf-8')

from iot_pkg.resource import add_resource
from iot_pkg.core import create_app


add_resource()
application = create_app()
