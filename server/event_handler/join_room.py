#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""数据库操作，将用户加入到指定房间的操作"""

from pprint import pprint
from common.message import MessageType
from server.broadcast import broadcast
import server.memory
from common.util import md5
from server.util import database
from server.util import add_target_type
from server.memory import *


def run(sc, parameters):
    user_id = server.memory.sc_to_user_id[sc]
    #异常处理判断
    if database.in_room(user_id, parameters):
        sc.send(MessageType.general_failure, '已经在群里了')
        return
    room = database.get_room(parameters)
    if room is None:
        sc.send(MessageType.general_failure, '群不存在')
        return
    if (not database.is_in_room_blacklist(user_id,parameters)):
        database.add_to_room(user_id, parameters)
        #contact_info操作码控制handle_contact函数，做前端添加聊天框操作
        sc.send(MessageType.contact_info, add_target_type(room, 1))
        room_members = database.get_room_members(parameters)
        for member in room_members:
            if member[0] in user_id_to_sc:
                server.memory.user_id_to_sc[member[0]].send(MessageType.query_room_users_result, [room_members, parameters])
        return
    else: 
        sc.send(MessageType.general_failure, '您已被该群管理员加入黑名单，如有疑问请联系群管理员')
        return
