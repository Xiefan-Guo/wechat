import server
import server.memory
import util.message


def run(sc, parameters):
    user_id = server.memory.sc_to_user_id[sc]

    uid = parameters[0]
    accepted = parameters[1]
    c = server.database.get_cursor()
    r = c.execute('SELECT 1 from friends where from_user_id=? and to_user_id=? and accepted=0', [uid, user_id])
    rows = r.fetchall()
    if len(rows) == 0:
        return

    if not accepted:
        c = server.database.get_cursor()
        c.execute('delete from friends where from_user_id=? and to_user_id=? and accepted=0', [uid, user_id])
        return

    if accepted:
        c = server.database.get_cursor()
        c.execute('update friends set accepted=1 where from_user_id=? and to_user_id=? and accepted=0', [uid, user_id])
        c = server.database.get_cursor()
        c.execute('insert into friends (from_user_id,to_user_id,accepted) values (?,?,1)', [user_id, uid])

        util.send_message(sc,util.message.MessageType.contact_info, server.add_target_type(server.database.get_user(uid), 0))

        if uid in server.memory.user_id_to_sc:
            util.send_message(server.memory.user_id_to_sc[uid],util.message.MessageType.contact_info, server.add_target_type(server.database.get_user(user_id), 0))
