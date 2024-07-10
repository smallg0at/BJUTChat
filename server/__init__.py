#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    server初始化函数
    首先一运行生成自己的服务器秘钥和证书
    建立socket进入监听状态
    select.select非阻断式处理数据包接收
    while循环中会不断刷新在线信息
"""

import socket
from common.config import get_config
import common.transmission.secure_channel
from server.event_handler import handle_event
from server.memory import *
import server.memory
from common.message import MessageType
from server.broadcast import broadcast
import select
from server.util import database
from pprint import pprint
import struct
import sys
import traceback
from common.cryptography import crypt
import logging
import socketio
import orjson
from nacl.public import PrivateKey, PublicKey, Box

"""生成证书"""
def gen_cert():
    crypt.gen_secret()

def run():
    logging.info('Server Launched. ')
    gen_cert()

    with open("public.pem", 'rb') as f:
        server_pub = f.read()
        f.close()
    with open("public.pem", 'rb') as f:
        server_priv = f.read()
        f.close()

    # config = get_config()
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # s.bind((config['server']['bind_ip'], config['server']['bind_port']))
    # s.listen(1)

    # print("Server listening on " + config['server']['bind_ip'] + ":" + str(config['server']['bind_port']))
    # logging.info("Server listening on " + config['server']['bind_ip'] + ":" + str(config['server']['bind_port']))

    bytes_to_receive = {}
    bytes_received = {}
    data_buffer = {}


    sio = socketio.Server(json=orjson)

    @sio.event
    def connect(sid, environ, auth):
        print(f'connecting: {sid}')
        sio.save_session(sid, {'ready': False})
        return True

    @sio.event
    def conn_ping1(sid, data):
        sio.save_session(sid, {'ready': False, 'client-pub': data})
        return server_pub

    @sio.event
    def conn_ping2(sid, data):  
        sio.save_session(sid, {'ready': True})

    @sio.event
    def login(sid, data):

        pass

    @sio.event
    def register(sid, data):
        pass

    @sio.event
    def client_echo(sid, data):
        pass

    @sio.event
    def add_friend(sid, data):
        pass
        
    @sio.event
    def resolve_friend_request(sid, data):
        pass

    @sio.event
    def send_message(sid, data):
        pass
    
    @sio.event
    def join_room(sid, data):
        pass

    @sio.event
    def create_room(sid, data):
        pass
                
    @sio.event
    def query_room_users(sid, data):
        pass

    @sio.event
    def bad(sid, data):
        pass

    @sio.event
    def del_friend(sid, data):
        pass
         
    # while True:
    #     rlist, wlist, xlist = select.select(list(map(lambda x: x.socket, scs)) + [s], [], [])

    #     for i in rlist:

    #         if i == s:
    #             # 监听socket为readable，说明有新的客户要连入
    #             sc = common.transmission.secure_channel.accept_client_to_secure_channel(s)
    #             try:
    #                 socket_to_sc[sc.socket] = sc
    #                 scs.append(sc)
    #                 bytes_to_receive[sc] = 0
    #                 bytes_received[sc] = 0
    #                 data_buffer[sc] = bytes()
    #             except Exception as e:
    #                 logging.exception(f"A user refused to be connected.")
                
    #             continue

    #         # 如果不是监听socket，就是旧的客户发消息过来了
    #         sc = socket_to_sc[i]

    #         if bytes_to_receive[sc] == 0 and bytes_received[sc] == 0:
    #             # 一次新的接收
    #             conn_ok = True
    #             first_4_bytes = ''
    #             try:
    #                 first_4_bytes = sc.socket.recv(4)
    #             except ConnectionError:
    #                 conn_ok = False

    #             if first_4_bytes == "" or len(first_4_bytes) < 4:
    #                 conn_ok = False

    #             if not conn_ok:
    #                 sc.close()
    #                 # 把他的连接信息移除
    #                 remove_sc_from_socket_mapping(sc)

    #             else:
    #                 data_buffer[sc] = bytes()
    #                 bytes_to_receive[sc] = struct.unpack('!i', first_4_bytes)[0]
    #                 print(f"Incoming a packet of length {bytes_to_receive[sc]}")

    #         buffer = sc.socket.recv(bytes_to_receive[sc] - bytes_received[sc])
    #         data_buffer[sc] += buffer
    #         bytes_received[sc] += len(buffer)

    #         if bytes_received[sc] == bytes_to_receive[sc] and bytes_received[sc] != 0:
    #             # 当一个数据包接收完毕
    #             bytes_to_receive[sc] = 0
    #             bytes_received[sc] = 0
    #             try:
    #                 data = sc.on_data(data_buffer[sc])
    #                 print(data['type'])
    #                 handle_event(sc, data['type'], data['parameters'])
    #             except:
    #                 pprint(sys.exc_info())
    #                 traceback.print_exc(file=sys.stdout)
    #                 pass
    #             data_buffer[sc] = bytes()
