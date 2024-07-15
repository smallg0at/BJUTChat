# #!/usr/bin/env python
# # -*- coding:utf-8 -*-

# """添加好友操作
#     首先获取sc对应user在数据库中信息，然后在异常检查之后控制数据库在
# friends表中插入一条信息且accept = 0表示未接受。接着发送操作码控制被请求方
# 和前端显示
# """

# import server.memory
# from pprint import pprint
# from common.message import MessageType
# from server.broadcast import broadcast
# from common.util import md5
# from server.util import database
# from server.memory import *


# def run(sc, parameters):
#     """
#     获取发送好友方信息，控制数据库执行添加好友操作，并发送add_friend_result
#     操作码控制前端显示，发送incoming_friend_request操作码让服务器给被请求方发送请求
#     """
#     #好友请求方user_id
#     username = parameters[0]
#     room_name = parameters[1]
#     user_id = sc_to_user_id[sc]

#     # parameters = [username,room_name]

#     c = database.get_cursor()
#     username = username.strip().lower()
#     room_name = room_name.strip().lower()

#     r = c.execute('SELECT id from users where username=?', [username]).fetchall()
#     if len(r) == 0:
#         sc.send(MessageType.invite_result, [False, '用户名不存在'])
#         return
    
#     r2 = c.execute('SELECT room_id from rooms where room_name=?' [room_name]).fetchall()
#     if len(r2) == 0:
#         sc.send(MessageType.invite_result, [False, '群不存在'])
#         return
    
#     #好友被加方uid
#     uid = r[0][0]

#     if uid == user_id:
#         sc.send(MessageType.invite__result, [False, '不能邀请自己入群'])
#         return

#     c = database.get_cursor()
#     r = c.execute('SELECT 1 from room_user where room_id=? and user_id=?', [uid, room_id]).fetchall()

#     if len(r) != 0:
#         sc.send(MessageType.add_friend_result, [False, '已经是好友/已经发送过好友请求'])
#         #上面这个列表为到了contact_form.py的parameters[0],[1]
#         return

#     c = database.get_cursor()
#     c.execute('insert into friends (from_user_id,to_user_id,accepted) values (?,?,0)', [user_id, uid]).fetchall()

#     sc.send(MessageType.add_friend_result, [True, ''])
#     if uid in user_id_to_sc:
#         user_id_to_sc[uid].send(MessageType.incoming_friend_request, database.get_user(user_id))


#暂且实现最基本的邀请入群功能，目前只支持老师强制邀请入群
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
            if (database.is_room_manager(inviter_id, room_id)):
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
