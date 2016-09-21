1、本项目框架为flask
2、第一次运行本项目：a、pip install -r requirements.txt  # 安装第三方包
				  b、python manage.py addnode you_conf.ini # 或者进入conf目录下的users.ini文件进行配置，添加(你的节点=你选择的配置文件)                  	获取你的节点：import platform; print platform.node()
				  c、python manage.py initdb  # 初始化数据库
				  d、python manage.py createuser -u my_name -p my_password # 创建一个后台用户，登录时候可用
				  e、python manage.py runserver		# 测试环境的启动方式
				  f、浏览器访问 127.0.0.1:5000
				  g、更多功能可查看manage.py
				  h、如需要更多功能支持请联系项目负责人
3、如果用gunicorn作为wsgi serve, 请将requirements.txt中gunicorn和gevent的注释取消，install完之后启动, 启动方式 gunicorn -c gun.py router:app
4、项目负责人：刘剑刚；联系电话：18268174851