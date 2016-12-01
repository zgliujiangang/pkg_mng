# /usr/bin/env python
# -*- coding: utf-8 -*-
# gunicorn的配置文件

chdir='..'

bind = "127.0.0.1:5000"
# backlog = 2048

workers = 4
worker_class = "gevent"
# timetout = 60

daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

errorlog = "-"
accesslog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

proc_name = None

# hooks如有需要请参考gunicorn文档