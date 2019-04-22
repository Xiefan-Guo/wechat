import server
import util

def run(sc, parameters):
    parameters[0] = parameters[0].strip().lower()
    c = server.database.get_cursor()
    r = c.execute('SELECT id,username from users where username=? and password=?', (parameters[0], util.md5(parameters[1])))
    rows = r.fetchall()

    if len(rows) == 0:
        util.send_message(sc,util.message.MessageType.login_failed)
        return

    user_id = rows[0][0]

    # 已经登入，踢下线
    if user_id in server.memory.user_id_to_sc:
        sc_old = server.memory.user_id_to_sc[user_id]
        util.send_message(sc_old,util.message.MessageType.server_kick)
        sc_old.close()
        server.memory.remove_sc_from_socket_mapping(sc_old)

    server.memory.sc_to_user_id[sc] = user_id
    server.memory.user_id_to_sc[user_id] = sc
    user = server.database.get_user(user_id)#得到用户信息，昵称。。。
    util.send_message(sc,util.message.MessageType.login_successful, user)


    login_bundle = {}

    # 发送好友请求
    frs = server.database.get_pending_friend_request(user_id)

    for fr in frs:
        util.send_message(sc,util.message.MessageType.incoming_friend_request, fr)

    # 发送好友列表
    frs = server.database.get_friends(user_id)
    login_bundle['friends'] = list(map(lambda x: server.add_target_type(x, 0), frs))

    for fr in frs:
        # 通知他的好友他上线了
        if fr['id'] in server.memory.user_id_to_sc:
            util.send_message(server.memory.user_id_to_sc[fr['id']],util.message.MessageType.friend_on_off_line, [True, user_id])
    login_bundle['messages'] = server.database.get_chat_history(user_id)
    util.send_message(sc,util.message.MessageType.login_bundle, login_bundle)
