# -*- coding: utf-8 -*-


import os
import click
import pprint
from wsgi import application


@click.group()
def cli():
    pass


@cli.command()
def initdb():
    # 初始化数据库表
    from iot_pkg.core import create_db
    db = create_db()
    pprint.pprint(db.get_tables_for_bind())
    db.drop_all()
    db.create_all()
    click.echo("Initialized the database")


@cli.command()
def dropdb():
    # 删除数据库
    from iot_pkg.core import create_db
    db = create_db()
    db.drop_all()
    click.echo("Dropped the database")


@cli.command()
def clearall():
    # 清除数据库以及删除程序包
    from iot_pkg.core import create_db
    from iot_pkg import settings
    db = create_db()
    db.drop_all()
    click.echo("Dropped the database")
    try:
        file_list = os.listdir(settings.FILE_PATH)
        for file in file_list:
            _file = os.path.join(settings.FILE_PATH, file)
            os.remove(_file)
            click.echo("Dropped file: %s" % file)
    except Exception as e:
        click.echo("删除文件失败")
        click.echo(str(e))
        click.echo("请手动删除所有文件")
    try:
        cache_files = os.listdir(settings.CACHE_PATH)
        for file in cache_files:
            _file = os.path.join(settings.CACHE_PATH, file)
            os.remove(_file)
            click.echo("Dropped cache: %s" % file)
    except Exception as e:
        click.echo("删除缓存失败")
        click.echo(str(e))
        click.echo("请手动删除所有缓存数据")
    finally:
        click.echo("Done...")


@cli.command()
@click.option("--host", "-h", default="127.0.0.1", help="run host")
@click.option("--port", "-p", default=5000, help="run port", type=int)
def runserver(host, port):
    # 启动项目
    application.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    cli()