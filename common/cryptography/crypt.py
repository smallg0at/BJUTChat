#!/usr/bin/env python
# -*- coding:utf-8 -*-

from random import randint
from common.config import get_config
from common.util import long_to_bytes
import hashlib
import nacl.utils
from nacl.public import PrivateKey, Box
import nacl.encoding



"""生成公私钥并保存到文件中"""
def gen_secret():

    private_self = PrivateKey.generate()
    public_self = private_self.public_key
    with open("private.pem", "wb") as f:
        f.write(private_self.encode(nacl.encoding.Base64Encoder))
        f.close()
    with open("public.pem", "wb") as f:
        f.write(public_self.encode(nacl.encoding.Base64Encoder))
        f.close()

    

# """生成共享密钥"""
# def get_shared_secret(their_secret):

#     with open("public.pem", "rb") as f:
#         pub = f.read()
#         f.close()

#     f = open("private.pem", "rb")
#     secret = int(f.read())
#     f.close()
#     return hashlib.sha256(long_to_bytes(int(their_secret) ** secret % modulus)).digest()

# """从证书中获取公钥"""
# def getpk_from_cert(cert):

#     str = cert.split()
#     return str[2]