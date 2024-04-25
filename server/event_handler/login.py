#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""服务器使用数据库验证客户端数据登录"""

from common.message import MessageType
from common.util import md5
from server.util import database
from server.util import add_target_type
from server.memory import *
from pprint import pprint


def run(sc, parameters):
    parameters[0] = parameters[0].strip().lower()
    c = database.get_cursor()
    r = c.execute('SELECT id,username from users where username=? and password=?', (parameters[0], md5(parameters[1])))
    rows = r.fetchall()

    if len(rows) == 0:
        sc.send(MessageType.login_failed)
        return

    user_id = rows[0][0]

    # 已经登入，踢下线
    if user_id in user_id_to_sc:
        sc_old = user_id_to_sc[user_id]
        sc_old.send(MessageType.server_kick)
        sc_old.close()
        remove_sc_from_socket_mapping(sc_old)

    sc_to_user_id[sc] = user_id
    user_id_to_sc[user_id] = sc
    user = database.get_user(user_id)
    sc.send(MessageType.login_successful, user)
    print('UserLogin: ',user_id)
    login_bundle = {}

    # 发送群列表
    rms = database.get_user_rooms(user_id)
    login_bundle['rooms'] = list(map(lambda x: add_target_type(x, 1), rms))
    # print('User groups:',rms)
    # for rm in rms:
    #     sc.send(MessageType.contact_info, add_target_type(rm, 1))

    # 发送好友请求
    frs = database.get_pending_friend_request(user_id)
    
    for fr in frs:
        sc.send(MessageType.incoming_friend_request, fr)

    # 发送好友列表
    frs = database.get_friends(user_id)

    login_bundle['friends'] = list(map(lambda x: add_target_type(x, 0), frs))
    print('User friends:',frs)


    login_bundle['messages'] = database.get_chat_history(user_id)
    print('Bundle sent. size', len(login_bundle))
    sc.send(MessageType.login_bundle, login_bundle)
