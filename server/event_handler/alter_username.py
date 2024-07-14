import server.memory
from pprint import pprint
from common.message import MessageType
from server.broadcast import broadcast
from common.util import md5
from server.util import database
from server.memory import *
from server.util import add_target_type

def run(sc, parameters):
    user_id = server.memory.sc_to_user_id[sc]
    c = database.get_cursor()
    new_username = parameters['new_username'].strip()
    if "drop" in new_username or len(new_username) == 0:
        sc.send(MessageType.general_failure, "用户名无效")
    c.execute("""UPDATE "main"."users"
              SET username=? WHERE id=?
              """)
    friends = database.get_friends(user_id)
    for friend in friends:
        if friend['online']:
            server.memory.user_id_to_sc[friend['id']].send(MessageType.del_info, user_id)
            server.memory.user_id_to_sc[friend['id']].send(MessageType.contact_info, add_target_type(friend, 0))

    rooms = database.get_user_rooms_id(user_id)
    for room in rooms:
        room_members = database.get_room_members(room)
        for member in room_members:
            if member['online']:
                server.memory.user_id_to_sc[member['id']].send(MessageType.query_room_users_result, [room_members, room])
            
    sc.send(MessageType.general_msg, "更改成功")