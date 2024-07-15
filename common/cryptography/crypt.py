#!/usr/bin/env python
# -*- coding:utf-8 -*-
import nacl.utils
from nacl.public import PrivateKey
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
