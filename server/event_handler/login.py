#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""服务器使用数据库验证客户端数据登录"""

from common.message import MessageType
from common.util import md5
from server.util import database
from server.util import add_target_type
from server.memory import *
import logging
logger = logging.getLogger(__name__)

def run(sc, parameters):
    parameters[0] = parameters[0].strip().lower()
    c = database.get_cursor()
    r = c.execute('SELECT id,username,school_id from users where school_id=? and password=?', (parameters[0], md5(parameters[1])))
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

    #若被禁止，则不允许登录
    if (user['is_banned'] == 1):
        sc.send(MessageType.user_is_banned)
        sc.close()
        remove_sc_from_socket_mapping(sc)
    else:    
        sc.send(MessageType.login_successful, user)
        logging.info('UserLogin: %s',user_id)
        login_bundle = {}

    # 发送群列表
    rms = database.get_user_rooms(user_id)
    login_bundle['rooms'] = list(map(lambda x: add_target_type(x, 1), rms))

    # 发送好友请求
    frs = database.get_pending_friend_request(user_id)
    
    for fr in frs:
        sc.send(MessageType.incoming_friend_request, fr)

    # 发送好友列表
    frs = database.get_friends(user_id)

    login_bundle['friends'] = list(map(lambda x: add_target_type(x, 0), frs))


    login_bundle['messages'] = database.get_chat_history(user_id)

    login_bundle['announcements'] = database.get_announcements()

    logging.info('Bundle sent.')
    sc.send(MessageType.login_bundle, login_bundle)
