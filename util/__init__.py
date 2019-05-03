import json,struct
from hashlib import md5 as _md5
from util.message import serialize_message


with open('config.json') as config_file:
    config = json.load(config_file)

def get_config():#得到配置信息
    return config


def send_message(socket,message_type, parameters=None):#发送信息，首先进行序列化
    data_to_encrypt = serialize_message(message_type, parameters)
    length_of_message = len(data_to_encrypt)

    state = socket.sendall(
        struct.pack('!L', length_of_message) + data_to_encrypt)
    return state

def md5(text): #用户密码加密
    m = _md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()