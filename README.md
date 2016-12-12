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