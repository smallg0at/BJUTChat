#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""生成大素数

先生成随机数，然后判断是否是素数
"""

# from random import randint
import sympy

""" 生成大素数 """
def generate_big_prime(n):
    return sympy.randprime(2048, pow(2,n))