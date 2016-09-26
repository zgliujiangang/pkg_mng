安装包更新系统
==============
### 框架
        flask+sqlalchemy
### 本地初次运行
        1. `pip install -r requirements.txt` 安装项目用到的第三方包
        2. 在conf目录下创建my.ini，将test.ini里面的配置拷贝到my.ini，pkg_path需要根据本地环境修改
        3. `python manage.py initdb` 初始化数据库
        4. `python manage.py createuser -u my_name -p my_password` 创建一个后台用户
        5. `python manage.py runserver` 本地启项目
        6. 浏览器访问 127.0.0.1:5000
        7. 更多功能可查看manage.py
        8. test.ini以及production.ini里的配置内容不能随意修改,若未创建本机的配置文件my.ini，则默认以test.ini启动
### 正式环境运行
        1. 参考上面1-5点
        2. 将requirements.txt中gunicorn和gevent的注释取消
        3. `pip install -r requirements.txt` 安装gevent和gunicorn
        4. `gunicorn -c gun.py router:app`
### 负责人
        姓名：刘剑刚    电话：18268174851