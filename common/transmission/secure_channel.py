#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
通过安全信道传输的消息格式
|--Length of Message Body(4Bytes)--|--Length of AES padding (1Byte)--|--AES IV (16Bytes)--|--MAC (32Bytes)--|--Message Body (CSON)--|
"""

import os
import socket
import struct

import nacl.encoding
from common.config import get_config
from common.cryptography import crypt
from common.message import serialize_message, deserialize_message, ByteArrayReader
from common.util import long_to_bytes
from pprint import pprint
from server.util import database
import logging
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import nacl
from nacl.encoding import Base64Encoder
import uuid

"""建立安全信道"""
class SecureChannel:

    def __init__(self, socket, opposite_public, self_private):
        # socket.setblocking(0)
        self.socket = socket
        
        self.box = Box(self_private, opposite_public)
    
        return

    def send(self, message_type, parameters=None):
        iv1 = bytes(os.urandom(16))
        data_to_encrypt = serialize_message(message_type, parameters)

        message = self.box.encrypt(data_to_encrypt)
        length_of_encrypted_message = len(message)
        packet = struct.pack('!i', length_of_encrypted_message) + message
        length_of_packet = len(packet)


        totalsent=0
        while totalsent < length_of_packet:
            try:
                sent = self.socket.send(packet[totalsent:totalsent+1024])
            except BlockingIOError as e:
                # sleep(0.05)
                continue
            print('sending', length_of_packet, 'Bytes, this time',sent,'Bytes')
            if sent == 0:
                logging.error("socket connection broken")
            totalsent = totalsent + sent
            
        
        return

    def on_data(self, data_array):

        decrypted_data = self.box.decrypt(data_array)
        return deserialize_message(decrypted_data)

    def close(self):
        self.socket.close()


def establish_secure_channel_to_server():
    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 131072)
    s.settimeout(5)
    s.connect((config['client']['server_ip'], int(config['client']['server_port'])))

            
    uuid = spawn_uuid()
    s.send(uuid.encode())

    # 接收服务器证书
    server_cert = s.recv(1024)

    # certname = "cert/" + uuid + ".pem"
    if not (os.path.exists('public.pem') and os.path.exists('private.pem')):
        # 生成私钥公钥和证书
        crypt.gen_secret()

    # 首次连接，给服务器发送证书
    with open('public.pem', 'rb') as f:
        client_cert = f.read()
        f.close()
    s.send(client_cert)

        


    server_pub = PublicKey(Base64Encoder.decode(server_cert))

    with open('private.pem', 'rb') as f:
        sc = SecureChannel(s, server_pub, PrivateKey(Base64Encoder.decode(f.read())))

    return sc


def accept_client_to_secure_channel(socket):
    conn, addr = socket.accept()

    # 首次连接，客户端会发送公钥
    try:
        uuid = conn.recv(1024)
        print(f"Incoming user with uuid {uuid.decode()}")
    except Exception as e:
        logging.error('SecureChannel: Failed to receive client uuid!')
        return 
    
    certname = "cert/" + uuid.decode() + "_cert.pem"

    # 把服务器的证书发送给客户端
    with open("public.pem", 'rb') as f:
        server_cert = f.read()
        f.close()

    conn.send(server_cert)

    try:
        client_cert = conn.recv(1024)
    except Exception as e:
        logging.error('SecureChannel: Failed to receive client cert!')
        return 
    
    try:
        with open(certname, 'wb') as f:
            f.write(client_cert)
            f.close()
    except Exception as e:
        print('SecureChannel: Failed to read remote key...')
        return
    
    client_pub = PublicKey(Base64Encoder.decode(client_cert))
    with open('private.pem', 'rb') as f:
        sc = SecureChannel(conn, client_pub, PrivateKey(Base64Encoder.decode(f.read())))
    return sc

# get local ip. Problematic, abandoned.
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    return ip

def spawn_uuid():
    if os.path.exists('uuid'):
        with open('uuid', 'r') as f:
            temp_uuid = f.read()
            f.close()
            return temp_uuid
    else:
        temp_uuid = str(uuid.uuid4())
        with open('uuid', 'w') as f:
            f.write(temp_uuid)
            f.close()
        return temp_uuid