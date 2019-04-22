import server
import util
import server.memory

def run(sc, parameters):
    user_id = server.memory.sc_to_user_id[sc]

    c = server.database.get_cursor()
    username = parameters.strip().lower()

    r = c.execute('SELECT id from users where username=?', [username]).fetchall()

    if len(r) == 0:
        util.send_message(sc,server.MessageType.add_friend_result, [False, '用户名不存在'])
        return

    uid = r[0][0]

    if uid == user_id:
        util.send_message(sc,server.MessageType.add_friend_result, [False, '不能加自己为好友'])
        return

    c = server.database.get_cursor()
    r = c.execute('SELECT 1 from friends where from_user_id=? and to_user_id=?', [user_id, uid]).fetchall()

    if len(r) != 0:
        util.send_message(sc,server.MessageType.add_friend_result, [False, '已经是好友/已经发送过好友请求'])
        return

    c = server.database.get_cursor()
    c.execute('insert into friends (from_user_id,to_user_id,accepted) values (?,?,0)', [user_id, uid]).fetchall()

    util.send_message(sc,server.MessageType.add_friend_result, [True, ''])

    if uid in server.memory.user_id_to_sc:
        util.send_message(server.memory.user_id_to_sc[uid],server.MessageType.incoming_friend_request, server.database.get_user(user_id))

