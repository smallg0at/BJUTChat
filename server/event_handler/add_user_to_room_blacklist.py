# #!/usr/bin/env python
# # -*- coding:utf-8 -*-

from pprint import pprint
from common.message import MessageType

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
    #身份检查,操作者必须为管理员,被加入黑名单的用户必须在群内
    if(database.is_room_manager(operator_id, room_id) or database.is_room_creator(operator_id, room_id)):
        if(database.in_room(user_id, room_id)):
            if((user_id==operator_id)and(database.is_room_creator(operator_id,room_id))):
               sc.send(MessageType.general_failure, '群主不能把自己加入黑名单并移出群聊')
               return
            else:     
                database.add_user_to_room_blacklist(user_id, room_id)
                database.remove_user_from_room(user_id, room_id)
                sc.send(MessageType.add_user_to_room_blacklist_result, [True, user_id, room_id])
                room_members = database.get_room_members(room_id)
                for member in room_members:
                    if member[0] in user_id_to_sc:
                        server.memory.user_id_to_sc[member[0]].send(MessageType.query_room_users_result, [room_members, room_id])
                user_id_to_sc[user_id].send(MessageType.del_info_group, database.get_room(room_id))
                user_id_to_sc[user_id].send(MessageType.general_msg, f"您已被移出群聊，并加入黑名单。群号：{room_id}")
        else: sc.send(MessageType.general_failure, '该用户必须在群内才能被加入黑名单')
    else: 
        sc.send(MessageType.general_failure, '只有管理员才能把用户加入群黑名单')



    

