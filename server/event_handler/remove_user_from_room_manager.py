# #!/usr/bin/env python
# # -*- coding:utf-8 -*-

from pprint import pprint
from common.message import MessageType
from server.broadcast import broadcast
import server.memory
from common.util import md5
from server.util import database
from server.util import add_target_type
from server.memory import *


def run(sc, parameters):
    #parameters = [user_id,room_id]
    user_id = parameters[0]
    room_id = parameters[1]
    operator_id = server.memory.sc_to_user_id[sc]
    #身份检查,操作者必须为群创建者,被剥夺管理员权限的用户必须在群内
    if(database.is_room_creator(operator_id, room_id)):
        if(database.is_room_manager(user_id, room_id)):   
            if(user_id == operator_id):
                sc.send(MessageType.general_failure, '群主的管理员权限不能被剥夺')
                return
            else: 
                database.remove_user_from_room_manager(user_id, room_id)
                sc.send(MessageType.remove_user_from_room_manager_result, [True, user_id, room_id])
                room_members = database.get_room_members(room_id)
                for member in room_members:
                    if member[0] in user_id_to_sc:
                        server.memory.user_id_to_sc[member[0]].send(MessageType.query_room_users_result, [room_members, room_id])
        else: sc.send(MessageType.general_failure, '该用户必须是管理员才能被剥夺管理员权限')
    else: 
        sc.send(MessageType.general_failure, '只有群主才能剥夺管理员权限')

    

    

