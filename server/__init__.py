import socket
from util import get_config
from server.events_handle import handle_event
from util.message import MessageType,deserialize_message
import select
import util
import server.database_handle as database
from pprint import pprint
import struct
import sys
import traceback
import server.memory

def add_target_type(obj, type):#给字典增加一个key
    obj['type'] = type
    return obj


def run():
    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#操作系统会在服务器socket被关闭或服务器进程终止后马上释放该服务器的端口，否则操作系统会保留几分钟该端口。
    host = socket.gethostname();
    post = 12345
    s.bind((host, post))
    s.listen(1)

    bytes_to_receive = {}
    bytes_received = {}
    data_buffer = {}

    while True:
        rlist, wlist, xlist = select.select(server.memory.scs + [s], [], [])#scs是所有连接过来的客户端，当客户端有活动时会被放入rlist列表
                                                                                             #发生错误的句柄放入x_list,第一个[]中的值原封不动的传递给w_list
        for i in rlist:

            if i == s:
                # 监听socket为s，说明有新的客户要连入
                sc, addr = s.accept()
                #sc = accept_client_to_secure_channel(s)
                #server.memory.socket_to_sc[sc] = sc
                server.memory.scs.append(sc)
                bytes_to_receive[sc] = 0
                bytes_received[sc] = 0
                data_buffer[sc] = bytes()
                continue

            # 如果不是监听socket，就是旧的客户发消息过来了
            sc = i#server.memory.socket_to_sc[i]

            if bytes_to_receive[sc] == 0 and bytes_received[sc] == 0:
                # 一次新的接收
                conn_ok = True
                first_4_bytes = ''
                try:
                    first_4_bytes = sc.recv(4)#先接收四个字节,代表数据包长度
                except ConnectionError:
                    conn_ok = False

                if first_4_bytes == "" or len(first_4_bytes) < 4:
                    conn_ok = False

                if not conn_ok:#当没有建立成功连接时，通知其好友其已经下线
                    sc.close()

                    if sc in server.memory.sc_to_user_id:
                        user_id = server.memory.sc_to_user_id[sc]
                        # 通知他的好友他下线了

                        frs = database.get_friends(user_id)
                        for fr in frs:
                            if fr['id'] in server.memory.user_id_to_sc:
                                util.send_message(server.memory.user_id_to_sc[fr['id']],MessageType.friend_on_off_line, [False, user_id])
                                #user_id_to_sc[fr['id']].send(MessageType.friend_on_off_line, [False, user_id])

                    # 把他的连接信息移除
                    server.memory.remove_sc_from_socket_mapping(sc)

                else:
                    data_buffer[sc] = bytes()#新的接收，建立新的字节流               #unpack解压出来的可能会有好几个之前被打包
                    bytes_to_receive[sc] = struct.unpack('!L', first_4_bytes)[0] #！代表大端格式，高位在高地址，L代表unsigned long类型

            buffer = sc.recv(bytes_to_receive[sc] - bytes_received[sc])#将要接收的减去已经接收的
            data_buffer[sc] += buffer
            bytes_received[sc] += len(buffer)

            if bytes_received[sc] == bytes_to_receive[sc] and bytes_received[sc] != 0:
                # 当一个数据包接收完毕，清空
                bytes_to_receive[sc] = 0
                bytes_received[sc] = 0
                try:
                    data = deserialize_message(data_buffer[sc])#将数据反序列化
                    handle_event(sc, data['type'], data['parameters'])#解析操作
                except:
                    pprint(sys.exc_info())
                    traceback.print_exc(file=sys.stdout)
                    pass
                data_buffer[sc] = bytes()
