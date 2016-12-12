# -*- coding: utf-8 -*-


from werkzeug import generate_password_hash, check_password_hash


class PasswordCrypto(object):
    # 密码的加密以及校验

    @staticmethod
    def hash(pwd):
        return generate_password_hash(pwd)

    @staticmethod
    def check(hash_pwd, pwd):
        return check_password_hash(hash_pwd, pwd)

    @classmethod
    def test_case(cls):
        password = "testpassword"
        hash_pwd = cls.hash(password)
        assert cls.check(hash_pwd, password), "密码验证方法有误"