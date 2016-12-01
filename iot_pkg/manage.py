# -*- coding: utf-8 -*-


import click


@click.group()
def cli():
	pass


@cli.command()
def initdb():
	# 初始化数据库表
	from application import db
	db.drop_all()
	db.create_all()
	click.echo("Initialized the database")


@cli.command()
def dropdb():
	# 删除数据库
	from application import db
	db.drop_all()
	click.echo("Dropped the database")


@cli.command()
@click.option("--user", "-u", help="admin username")
@click.option("--pwd", "-p", help="admin password")
def createuser(user, pwd):
	# 创建后台用户
	from _global import db
	from models.user import User
	from werkzeug import generate_password_hash
	print db
	pwd_hash = generate_password_hash(pwd)
	user = User(user, pwd_hash)
	db.session.add(user)
	db.session.commit()
	click.echo("create user:%s successfully!" % user)


@cli.command()
@click.option("--user", "-u", help="admin username")
def dropuser(user):
	# 删除后台用户
	from router import db
	from models.user import User
	user = User.query.filter_by(name=user).first()
	db.session.delete(user)
	db.session.commit()
	click.echo("drop user:%s successfully" % username)


@cli.command()
def clearall():
	# 清除数据库以及删除程序包
	import os
	from _global import config
	from router import db
	db.drop_all()
	click.echo("Dropped the database")
	pkg_path = config.get("flask", "pkg_path")
	pkg_list = os.listdir(pkg_path)
	try:
		for pkg in pkg_list:
			_pkg = os.path.join(pkg_path, pkg)
			os.remove(_pkg)
			click.echo("Dropped pkg: %s" % pkg)
	except Exception as e:
		click.echo("删除程序包失败")
		click.echo(str(e))
		click.echo("请手动删除所有程序包")
	finally:
		click.echo("Done...")


@cli.command()
@click.option("--host", "-h", default="127.0.0.1", help="run host")
@click.option("--port", "-p", default=5000, help="run port", type=int)
def runserver(host, port):
	# 启动项目
	from router import app
	app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
	cli()