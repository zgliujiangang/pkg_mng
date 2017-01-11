# -*- coding: utf-8 -*-


import random


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'):
    return ''.join(random.choice(allowed_chars) for i in range(length))