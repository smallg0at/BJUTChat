#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""操作数据库创建房间，新增数据"""

from common.message import MessageType
import server.memory
from server.util import database
from server.util import add_target_type
import time


def run(sc, parameters):
    user_id = server.memory.sc_to_user_id[sc]
    c = database.get_cursor()
    c.execute("insert into rooms (room_name,created_time,room_creator) values (?,?,?)", [parameters,int(round(time.time() * 1000)),user_id])
    sc.send(MessageType.contact_info, add_target_type(database.get_room(c.lastrowid), 1))
    database.add_to_room(user_id, c.lastrowid, 1)
    sc.send(MessageType.general_msg, '创建成功，群号为：' + str(c.lastrowid))