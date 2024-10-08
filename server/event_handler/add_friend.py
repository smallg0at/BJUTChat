#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""添加好友操作
    首先获取sc对应user在数据库中信息，然后在异常检查之后控制数据库在
friends表中插入一条信息且accept = 0表示未接受。接着发送操作码控制被请求方
和前端显示
"""


from common.message import MessageType

from common.util import md5
from server.util import database
from server.memory import *
from server.util import add_target_type


def run(sc, parameters):
    """
    获取发送好友方信息，控制数据库执行添加好友操作，并发送add_friend_result
    操作码控制前端显示，发送incoming_friend_request操作码让服务器给被请求方发送请求
    """
    #好友请求方user_id
    user_id = sc_to_user_id[sc]

    # parameters = username

    c = database.get_cursor()
    username = parameters.strip().lower()

    r = c.execute('SELECT id from users where school_id=?', [username]).fetchall()

    if len(r) == 0:
        sc.send(MessageType.add_friend_result, [False, '学工号不存在'])
        return

    #好友被加方uid
    uid = r[0][0]

    if uid == user_id:
        sc.send(MessageType.add_friend_result, [False, '不能加自己为好友'])
        return

    c = database.get_cursor()
    r = c.execute('SELECT 1 from friends where from_user_id=? and to_user_id=?', [user_id, uid]).fetchall()

    if len(r) != 0:
        sc.send(MessageType.add_friend_result, [False, '已经是好友/已经发送过好友请求'])
        #上面这个列表为到了contact_form.py的parameters[0],[1]
        return

    
    c = database.get_cursor()
    if database.is_teacher(user_id) and not database.is_teacher(uid):
        c.execute('insert into friends (from_user_id,to_user_id,accepted) values (?,?,1)', [user_id, uid]).fetchall()
        c.execute('insert into friends (to_user_id,from_user_id,accepted) values (?,?,1)', [user_id, uid])
        #给请求方发送contact_info创建好友列表
        sc.send(MessageType.contact_info, add_target_type(database.get_user(uid), 0))
        #被请求方创建好友列表
        if uid in user_id_to_sc:
            user_id_to_sc[uid].send(MessageType.contact_info, add_target_type(database.get_user(user_id), 0))
        sc.send(MessageType.add_friend_result, [True, 'force'])
    else:
        c.execute('insert into friends (from_user_id,to_user_id,accepted) values (?,?,0)', [user_id, uid]).fetchall()
        sc.send(MessageType.add_friend_result, [True, ''])
        if uid in user_id_to_sc:
            user_id_to_sc[uid].send(MessageType.incoming_friend_request, database.get_user(user_id))
        
