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
    #身份检查,操作者必须为管理员,被踢出的用户必须在群内
    if(database.is_room_manager(operator_id, room_id)):
        if(database.in_room(user_id, room_id)):    
            database.remove_user_from_room(user_id, room_id)
            sc.send(MessageType.remove_user_from_room_result, [True, user_id, room_id])
        else: 
            sc.send(MessageType.general_failure, '该用户必须在群内才能被移出群聊')
            return
    #非管理员能将自己踢出群聊
    else: 
        if(user_id!=operator_id):
            sc.send(MessageType.general_failure, '只有管理员才能将用户移出群聊')
            return
        else:
            if(database.in_room(operator_id, room_id)):    
                database.remove_user_from_room(operator_id, room_id)
                sc.send(MessageType.remove_user_from_room_result, [True, operator_id, room_id])
            else:sc.send(MessageType.general_failure, '你必须在群内才能退出群聊')
            return
    
    room_members = database.get_room_members(room_id)
    for member in room_members:
            if member[0] in user_id_to_sc:
                server.memory.user_id_to_sc[member[0]].send(MessageType.query_room_users_result, [room_members, room_id])

    
    user_id_to_sc[user_id].send(MessageType.del_info_group, database.get_room(room_id))
    user_id_to_sc[user_id].send(MessageType.general_msg, f"您已被移出群聊。群号：{room_id}")
    

