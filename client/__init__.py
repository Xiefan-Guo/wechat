import _thread,socket
from tkinter import messagebox
import tkinter as tk
from client.forms.login_form import LoginForm
import select,struct
import util
import sys
from pprint import pprint
import traceback
import client.memory


# 消息处理 0 - 文字消息 1 - 图片消息
def gen_last_message(obj):
    prefix = ''
    if obj['target_type'] == 1:
        prefix = obj['sender_name'] + ':'
    if obj['message']['type'] == 0:
        return prefix + obj['message']['data'].replace('\n', ' ')
    if obj['message']['type'] == 1:
        return prefix + '[图片消息]'

#socket
def socket_listener_thread(sc, tk_root):
    bytes_to_receive = 0
    bytes_received = 0
    data_buffer = bytes()
    while True:
        rlist, wlist, xlist = select.select([sc], [sc], [])
        if len(rlist):
            if bytes_to_receive == 0 and bytes_received == 0:
                # 一次新的接收
                conn_ok = True
                first_4_bytes = ''
                try:
                    first_4_bytes = sc.recv(4)
                except ConnectionError:
                    conn_ok = False
                if first_4_bytes == "" or len(first_4_bytes) < 4:
                    conn_ok = False
                if not conn_ok:
                    print('服务器已被关闭')
                    messagebox.showerror("出错了，服务器已经被关闭")
                    tk_root.destroy()
                else:
                    data_buffer = bytes()
                    bytes_to_receive = struct.unpack('!L', first_4_bytes)[0]
            # 接收数据、拼成块
            buffer = sc.recv(bytes_to_receive - bytes_received)
            data_buffer += buffer
            bytes_received += len(buffer)
            if bytes_received == bytes_to_receive:
                # 当一个数据包接收完毕
                bytes_to_receive = 0
                bytes_received = 0
                try:
                    data = util.message.deserialize_message(data_buffer)
                    # 处理general failure
                    if data['type'] == util.message.MessageType.general_failure:
                        messagebox.showerror("出错了", data['parameters'])
                    # 处理general message
                    if data['type'] == util.message.MessageType.general_msg:
                        messagebox.showinfo("消息", data['parameters'])
                    if data['type'] == util.message.MessageType.server_kick:
                        messagebox.showerror("出错了", '您的账户在别处登入')
                        tk_root.destroy()
                    if data['type'] == util.message.MessageType.server_echo:
                        pprint(['server echo', data['parameters']])
                    # 处理on_new_message
                    if data['type'] == util.message.MessageType.on_new_message:
                        digest_message(data['parameters'])
                    for func in client.memory.callback_funcs:
                        func(data)
                except:
                    pprint(sys.exc_info())
                    traceback.print_exc(file=sys.stdout)
                    pass

#消息处理
def digest_message(data, update_unread_count=True):
    # 放入 chat_history
    if data['target_id'] not in client.memory.chat_history[
        data['target_type']]:
        client.memory.chat_history[data['target_type']][
            data['target_id']] = []
    client.memory.chat_history[data['target_type']][
        data['target_id']].append(data)
    # 更新 last_message
    client.memory.last_message[data['target_type']][
        data['target_id']] = gen_last_message(
        data)
    # 更新 last_message_timestamp
    client.memory.last_message_timestamp[data['target_type']][
        data['target_id']] = data[
        'time']
    # 更新 unread_message_count
    if data['target_id'] not in client.memory.unread_message_count[
        data['target_type']]:
        client.memory.unread_message_count[data['target_type']][
            data['target_id']] = 0
    if data['target_id'] not in client.memory.window_instance[
        data['target_type']]:
        if update_unread_count:
            client.memory.unread_message_count[data['target_type']][
                data['target_id']] += 1
    # 更新contacts
    client.memory.contact_window[0].refresh_contacts()
    # 通知聊天窗口
    for item in client.memory.message_listeners:
        if item['target_type'] == data['target_type'] and item['target_id'] == \
                data['target_id']:
            item['func'](data)


def add_listener(func):
    client.memory.callback_funcs.append(func)


def remove_listener(func):
    client.memory.callback_funcs.remove(func)


func_to_tuple = {}


def add_message_listener(target_type, target_id, func):
    func_to_tuple[func] = {'target_type': target_type, 'target_id': target_id, 'func': func}
    client.memory.message_listeners.append(func_to_tuple[func])


def remove_message_listener(func):
    if func in func_to_tuple:
        client.memory.message_listeners.remove(func_to_tuple[func])

def run():
    root = tk.Tk()
    client.memory.tk_root = root
    try:
        client.memory.sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()  # 获取本地主机名
        port = 12345  # 设置端口号
        client.memory.sc.connect((host, port))
        #sc = establish_secure_channel_to_server()
    except ConnectionError:
        messagebox.showerror("出错了", "无法连接到服务器")
        exit(1)
    _thread.start_new_thread(socket_listener_thread, (client.memory.sc, root))
    login = tk.Toplevel()
    LoginForm(master=login)
    root.withdraw()
    root.mainloop()
    try:
        root.destroy()
    except tk.TclError:
        pass
