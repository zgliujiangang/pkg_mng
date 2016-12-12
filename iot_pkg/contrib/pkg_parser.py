# -*- coding: utf-8 -*-


import re
import io
import zipfile
import biplist
import subprocess
from iot_pkg.contrib.file_storage import File


class PackageParser(object):

    def __init__(self):
        self.parse_funcs = {}

    def register(self, *suffix_ls):
        def decorator(func):
            for suffix in suffix_ls:
                self.parse_funcs[suffix] = func
            return func
        return decorator

    def start_parse(self, pkg_file):
        assert isinstance(pkg_file, File), "传入的参数不是一个File对象"
        parse_func = self.parse_funcs.get(pkg_file.filename.split(".")[-1])
        if parse_func:
            pkg_info = parse_func(pkg_file)
            pkg_info = pkg_info if isinstance(pkg_info, dict) else {}
            return pkg_info
        else:
            print "不能识别的文件类型"
            return {}


pkg_parser = PackageParser()


@pkg_parser.register("apk")
def parse_android(pkg_file):
    # 运行这段代码前请先安装android sdk build-tool:aapt，并且将aapt放入环境变量中
    try:
        cmd = "aapt dump badging %s" % pkg_file.save_path
        info = subprocess.check_output(cmd, shell=True)
        regx = re.compile(r"package: name='(?P<name>.*?)' versionCode='(?P<v_code>.*?)' versionName='(?P<v_name>.*?)'")
        match = regx.search(info).groupdict()
        print match
        return match
    except subprocess.CalledProcessError as e:
        print str(e)
        print "解析apk文件出错"
        return {}
    except Exception as e:
        print e
        return {}


@pkg_parser.register("ipa")
def parse_ios(pkg_file):
    ipa_file = zipfile.ZipFile(pkg_file.save_path)
    plist_path = None
    regx = re.compile(r'Payload/[^/]*.app/Info.plist')
    for path in ipa_file.namelist():
        m = regx.match(path)
        if m is not None:
            plist_path = m.group()
            break
    if not plist_path:
        return None
    plist_data = ipa_file.read(plist_path)
    fp = io.BytesIO(plist_data)
    info = biplist.readPlist(fp)
    fp.close()
    print info
    return info