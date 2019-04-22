import server
import server.memory
import time
import util
from util.message import _serialize_dict



def run(sc, parameters):
    # pprint(parameters)
    user_id = server.memory.sc_to_user_id[sc]
    sender = server.database.get_user(user_id)

    # target只是dispatch用

    # target_id延后做，对于发送方和接收方不一样
    message = {"message": parameters['message'], 'sender_id': user_id,
               'sender_name': sender['nickname'],
               'target_type': parameters['target_type'],
               'time': int(round(time.time() * 1000))}

    if parameters['target_type'] == 0:
        # 私聊
        if not server.database.is_friend_with(user_id, parameters['target_id']):
            util.send_message(sc,util.message.MessageType.general_failure, '还不是好友')
            #sc.send(MessageType.general_failure, '还不是好友')
            return

        # 给发送方发回执
        message['target_id'] = parameters['target_id']
        util.send_message(server.memory.user_id_to_sc[user_id],util.message.MessageType.on_new_message, message)
        server.database.add_to_chat_history(user_id, message['target_id'], message['target_type'],
                                     _serialize_dict(message),
                                     True)

        # 给接收方发消息，存入聊天记录
        message['target_id'] = user_id
        sent = False
        if parameters['target_id'] in server.memory.user_id_to_sc:
            sent = True
            util.send_message(server.memory.user_id_to_sc[parameters['target_id']],util.message.MessageType.on_new_message, message)

        server.database.add_to_chat_history(parameters['target_id'], message['target_id'], message['target_type'],
                                     _serialize_dict(message),
                                     sent)

