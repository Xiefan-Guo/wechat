from tkinter import *
from util import get_config
import util
from util import send_message as sendMessage
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from PIL import ImageTk
import client
import os
import datetime


class ChatForm(client.tk.Frame):
    font_color = "#000000"
    font_size = 10
    user_list = []
    tag_i = 0
    #关闭listener
    def remove_listener_and_close(self):
        client.remove_message_listener(self.message_listener)
        client.remove_listener(self.socket_listener)
        self.master.destroy()
        if self.target['id'] in client.memory.window_instance[self.target['type']]:
            del client.memory.window_instance[self.target['type']][self.target['id']]
    #listener
    def message_listener(self, data):
        self.digest_message(data)
    #socket
    def socket_listener(self, data):
        if data['type'] == util.message.MessageType.query_users_result:
            if data['parameters'][1] != self.target['id']:
                return
            # [id, nickname, online, username]
            self.user_list = data['parameters'][0]
            self.refresh_user_listbox()

    #刷新列表信息
    def refresh_user_listbox(self):
        # [id, nickname, online, username]
        self.user_listbox.delete(0, END)
        self.user_list.sort(key=lambda x: x[2])
        for user in self.user_list:
            self.user_listbox.insert(0, user[1] + ("(ON-line)" if user[2] else "(OFF-line)"))
            self.user_listbox.itemconfig(0, {'fg': ("green" if user[2] else "red")})
    #消息处理
    def digest_message(self, data):
        time = datetime.datetime.fromtimestamp(
            int(data['time']) / 1000
        ).strftime('%Y-%m-%d %H:%M:%S')
        self.append_to_chat_box(data['sender_name'] + "  " + time + '\n',
                                ('me' if client.memory.current_user['id'] == data[
                                    'sender_id'] else 'them'))
        # type 0 - 文字消息 1 - 图片消息
        if data['message']['type'] == 0:
            self.tag_i += 1
            self.chat_box.tag_config('new' + str(self.tag_i),
                                     lmargin1=16,
                                     lmargin2=16,
                                     foreground=data['message']['fontcolor'],
                                     font=(None, data['message']['fontsize']))
            self.append_to_chat_box(data['message']['data'] + '\n',
                                    'new' + str(self.tag_i))
        if data['message']['type'] == 1:
            client.memory.tk_img_ref.append(ImageTk.PhotoImage(data=data['message']['data']))
            self.chat_box.image_create(END, image=client.memory.tk_img_ref[-1], padx=16, pady=5)
            self.append_to_chat_box('\n', '')

    def __init__(self, target, master=None):
        super().__init__(master)
        self.master = master
        self.target = target
        self.user_listbox = client.tk.Listbox(self, bg='blue')
        self.master.iconbitmap('F:\pycharm_python\wechat\client\image\\wechat.ico')
        client.add_listener(self.socket_listener)
        client.memory.unread_message_count[self.target['type']][self.target['id']] = 0
        client.memory.contact_window[0].refresh_contacts()
        master.resizable(width=True, height=True)
        master.geometry('660x500')
        master.minsize(520, 370)
        self.sc = client.memory.sc
        if self.target['type'] == 0:
            self.master.title(self.target['nickname'])
        self.right_frame = client.tk.Frame(self, bg='white')
        self.right_frame.pack(side=LEFT, expand=True, fill=BOTH)
        self.input_frame = client.tk.Frame(self.right_frame, bg='white')
        self.input_textbox = ScrolledText(self.right_frame, height=10)
        self.input_textbox.bind("<Control-Return>", self.send_message)
        self.send_btn = client.tk.Button(self.input_frame, text='Enter', bg='green',  width=10, height=1,command=self.send_message)
        self.send_btn.pack(side=RIGHT, expand=False)
        self.image_btn = client.tk.Button(self.input_frame, text='发送图片',bg='green',  width=10, height=1,command=self.send_image)
        self.image_btn.pack(side=LEFT, expand=False)
        self.chat_box = ScrolledText(self.right_frame, bg='white')
        self.input_frame.pack(side=BOTTOM, fill=X, expand=False)
        self.input_textbox.pack(side=BOTTOM, fill=X, expand=False, padx=(0, 0), pady=(0, 0))
        self.chat_box.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.chat_box.bind("<Key>", lambda e: "break")
        self.chat_box.tag_config("default", lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_box.tag_config("me", foreground="green", spacing1='5')
        self.chat_box.tag_config("them", foreground="blue", spacing1='5')
        self.chat_box.tag_config("message", foreground="black", spacing1='0')
        self.chat_box.tag_config("system", foreground="grey", spacing1='0',
                                 justify='center',
                                 font=(None, 8))
        self.pack(expand=True, fill=BOTH)
        client.add_message_listener(self.target['type'], self.target['id'], self.message_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_listener_and_close)
        if target['id'] in client.memory.chat_history[self.target['type']]:
            for msg in client.memory.chat_history[self.target['type']][target['id']]:
                self.digest_message(msg)
            self.append_to_chat_box('- 以上是历史消息 -\n', 'system')
    #更新消息框
    def append_to_chat_box(self, message, tags):
        self.chat_box.insert(client.tk.END, message, [tags, 'default'])
        self.chat_box.update()
        self.chat_box.see(client.tk.END)
    #发送信息
    def send_message(self, _=None):
        message = self.input_textbox.get("1.0", END)
        if not message or message.replace(" ", "").replace("\r", "").replace("\n", "") == '':
            return
        #config = get_config()
        flag = os.system('ping -n 1 -l 1 %s' %(get_config()['client']['server_ip']))
        #0-网络畅通
        if flag==0:
            sendMessage(self.sc,util.message.MessageType.send_message,
                     {'target_type': self.target['type'], 'target_id': self.target['id'],
                      'message': {
                          'type': 0,
                          'data': message.strip().strip('\n'),
                          'fontsize': self.font_size,
                          'fontcolor': self.font_color
                      }
                      })
        # #1-无法连接服务器
        else:
            self.append_to_chat_box('\n'+'[该信息发送失败] '+message.strip().strip('\n') + '\n',
                                    'new' + str(self.tag_i))
        self.input_textbox.delete("1.0", END)
        return 'break'

    #发送图片
    def send_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image Files",
                                                          ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.JPG", "*.JPEG",
                                                           "*.PNG", "*.GIF"]),
                                                         ("All Files", ["*.*"])])
        if filename is None or filename == '':
            return
        with open(filename, "rb") as imageFile:
            f = imageFile.read()
            b = bytearray(f)
            config = get_config()
            flag = os.system('ping -n 1 -l 1 %s' % (config['client']['server_ip']))
            #0-网络畅通
            if flag == 0:
                sendMessage(self.sc,util.message.MessageType.send_message,
                         {'target_type': self.target['type'], 'target_id': self.target['id'],
                          'message': {'type': 1, 'data': b}})
            #1-无法连接服务器
            else:
                self.append_to_chat_box('\n' + '[图片发送失败] '+'\n',
                                        'new' + str(self.tag_i))
