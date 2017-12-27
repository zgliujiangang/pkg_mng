安装包更新系统
==============
### 框架
        flask+sqlalchemy
### 本地运行
        1. `pip install -r requirements.txt` 安装项目用到的第三方包
        2. `cp iot_pkg/settings.py.sample iot_pkg/settings.py` 需要根据本地环境修改
        3. `python manage.py initdb` 初始化数据库
        4. `python manage.py runserver` 本地启项目
        5. 浏览器访问 127.0.0.1:5000
        6. 更多功能可查看manage.py
### 提示
        1、运行此服务需要本地安装aapt，并且将aapt加入环境变量中
### 代码
        1.iot_pkg/models里面包含了User(用户),Project(项目),Package(安装包),Channel(渠道),Counter(访问计数器)的数据库映射模型
        2.iot_pkg/resource.py里面包含了系统所有的url
        3.iot_pkg/resources/里面是系统业务处理层(view),包含了用户的增删查改、项目的增删查改、渠道的增删查改、安装包的增删查改、文件的上传功能
        4.iot_pkg/contrib/里面包含了系统的用户认证、密码加解密、文件存储、安装包自动解析等工具类
        5.iot_pkg/utils/里面包含了简单的缓存类
        6.本系统使用的数据库为sqlite, 可以使用命令行sqlite3 pkg.db进入数据库
        7.本系统利用文件缓存数据
        8.wsgi.py提供wsgi协议的应用application
        9.线上部署服务器：139.224.0.207
        10.线上部署方式：gunicorn + flask
        11.线上启动命令行：/home/exingcai/.Envs/iot_pkg/bin/python2 /home/exingcai/.Envs/iot_pkg/bin/gunicorn -c gunicorn.py wsgi:application
        12.swagger地址: /api/doc.html