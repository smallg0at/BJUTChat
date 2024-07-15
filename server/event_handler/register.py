#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    服务器控制数据库注册，删除了空白字符并将英文字符小写。
"""

from common.message import MessageType

from common.util import md5

from server.util import database

def run(sc, parameters):
    parameters[0] = parameters[0].strip()
    parameters[1] = parameters[1].strip()
    parameters[2] = parameters[2].strip().lower()

    if 'drop ' in parameters[2] or 'select ' in parameters[2]:
        sc.send(MessageType.general_failure, "学工号无效")
        return
    
    c = database.get_cursor()
    r = c.execute('SELECT * from users where school_id=?', [parameters[2]])
    rows = r.fetchall()



    if len(rows) > 0:
        sc.send(MessageType.school_id_taken)
        return

    if len(parameters[0]) <= 0 or len(parameters[0]) > 25:
        sc.send(MessageType.general_failure, "用户名无效")
        return
    
    if len(parameters[1]) <= 0 or len(parameters[1]) > 25:
        sc.send(MessageType.general_failure, "密码无效")
        return
    
    if len(parameters[2]) <= 0 or len(parameters[2]) > 15:
        sc.send(MessageType.general_failure, "学工号无效")
        return
    
    if parameters[3] not in ['男', '女', '保密']:
        sc.send(MessageType.general_failure, "性别无效")
        return
    
    if parameters[4] not in ['0', '1', 0, 1]:
        sc.send(MessageType.general_failure, "角色无效")
        return


    c = database.get_cursor()
    c.execute('INSERT into users (username, password, school_id, sex,role) values (?,?,?,?,?)',
              [parameters[0], md5(parameters[1]), parameters[2], parameters[3], parameters[4]])
    sc.send(MessageType.register_successful, c.lastrowid)

