#暂且实现最基本的邀请入群功能，目前只支持老师强制邀请入群
"""数据库操作，将用户加入到指定房间的操作"""

from common.message import MessageType

import server.memory
from server.util import database
from server.util import add_target_type
from server.memory import *

def run(sc, parameters):
    #parameters = [username,room_name]
   
    inviter_id = server.memory.sc_to_user_id[sc]

    c = database.get_cursor()
    school_id = parameters['school_id'].strip().lower()
    r = c.execute('SELECT id from users where school_id=?', [school_id]).fetchall()
    if len(r) == 0:
        sc.send(MessageType.general_failure, '所邀请用户名不存在')
        return
    uid = r[0][0]
    if (uid == inviter_id):
        sc.send(MessageType.general_failure, '不能邀请自己进群')
        return
    
    room_name = parameters['room_name'].strip().lower()

    user_id = database.user_schoolid_to_id(school_id)
    room_id = database.roomname_to_id(room_name)
    
        
    #异常处理判断
    if database.in_room(user_id, room_id):
        sc.send(MessageType.general_failure, '已经在群里了')
        return
    room = database.get_room(room_id)
    if room is None:
        sc.send(MessageType.general_failure, '群不存在')
        return
    #老师能强制添加用户入群，如果被邀请用户在黑名单中，则自动将其移出黑名单
    if (database.is_teacher(inviter_id)):
        if(database.is_in_room_blacklist(user_id,room_id)):
            database.remove_user_from_room_blacklist(user_id,room_id)
        database.add_to_room(user_id, room_id)
        #contact_info操作码控制handle_contact函数，做前端添加聊天框操作
        sc.send(MessageType.query_room_users_result, [database.get_room_members(room_id), room_id])
        sc.send(MessageType.general_msg, f'强制添加成功：{school_id}')
        if user_id in user_id_to_sc:
            user_id_to_sc[user_id].send(MessageType.contact_info, add_target_type(room, 1))
    else:
        #若被邀请用户在黑名单内，则只有管理员或老师能邀请入群，并自动解除黑名单，管理员只能邀请自己的好友入群
        if(database.is_in_room_blacklist(user_id,room_id)):
            if (database.is_room_manager(inviter_id, room_id) or database.is_room_creator(inviter_id, room_id)):
                if (not(database.is_friend_with(inviter_id,uid))):
                    sc.send(MessageType.general_failure, '您不能邀请非好友入群')
                    return
                else:
                    database.add_to_room(user_id, room_id)
                    database.remove_user_from_room_blacklist(user_id,room_id)
                    #contact_info操作码控制handle_contact函数，做前端添加聊天框操作
                    if user_id in user_id_to_sc:
                        user_id_to_sc[user_id].send(MessageType.contact_info, add_target_type(room, 1))
                    sc.send(MessageType.general_msg, f'添加成功：{school_id}')
            else:
                sc.send(MessageType.general_failure, '只有管理员能邀请被加入黑名单的用户入群')
                return
        #若不在黑名单内，则普通用户可邀请自己好友入群
        else:
            if (not(database.is_friend_with(inviter_id,uid))):
                sc.send(MessageType.general_failure, '您不能邀请非好友入群')
                return
            else:
                database.add_to_room(user_id, room_id)
                #contact_info操作码控制handle_contact函数，做前端添加聊天框操作
                if user_id in user_id_to_sc:
                    user_id_to_sc[user_id].send(MessageType.contact_info, add_target_type(room, 1))
                sc.send(MessageType.general_msg, f'添加成功：{school_id}')
    
        room_members = database.get_room_members(room_id)
        for member in room_members:
            if member[0] in user_id_to_sc:
                server.memory.user_id_to_sc[member[0]].send(MessageType.query_room_users_result, [room_members, room_id])
