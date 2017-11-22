create table pkg_package_migrate as select * from pkg_package;
drop table pkg_package;
/* python manage.py update 创建新的pkg_package 表*/
insert into pkg_package select * from pkg_package_migrate;
update pkg_package set channel='' where id>=1;