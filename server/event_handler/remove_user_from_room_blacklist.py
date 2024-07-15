# # #!/usr/bin/env python
# # # -*- coding:utf-8 -*-

#需求更改，此事件处理器废除
# from pprint import pprint
# from common.message import MessageType
# from server.broadcast import broadcast
# import server.memory
# from common.util import md5
# from server.util import database
# from server.util import add_target_type


# def run(sc, parameters):
#     #parameters = [user_id,room_id]
#     user_id = parameters[0]
#     room_id = parameters[1]
#     operator_id = server.memory.sc_to_user_id[sc]
#     #身份检查,操作者必须为管理员,被移出黑名单的用户必须在黑名单内
#     if(database.is_room_manager(operator_id, room_id)):
#         if(database.is_in_room_blacklist(user_id, room_id)):    
#             database.remove_user_from_room_blacklist(user_id, room_id)
#             sc.send(MessageType.remove_user_from_room_blacklist_result, [True, user_id, room_id])
#         else: sc.send(MessageType.general_failure, '该用户必须在黑名单中才能被移出')
#     else: 
#         sc.send(MessageType.general_failure, '只有管理员才能把用户移出群黑名单')

    

