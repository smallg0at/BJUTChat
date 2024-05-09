#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""生成大素数

先生成随机数，然后判断是否是素数
"""

# from random import randint
import sympy

""" 生成大素数 """
def generate_big_prime(n):
    return sympy.randprime(2048, 115792089237316195423570985008687907852837564279074904382605163141518161494336)