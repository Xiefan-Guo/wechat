import tkinter as tk
import time
from tkinter import messagebox
from util.message import _deserialize_any
from pypinyin import lazy_pinyin
import util
from tkinter import *
from client.components.gui import Chat_record,Chat_member,Chat_main
from client.forms.chat_form import ChatForm
from tkinter import Toplevel
import datetime
import client
from tkinter import simpledialog
from util import send_message as sendMessage

class ContactsForm(tk.Frame):
    bundle_process_done = False
    #关闭listener
    def remove_socket_listener_and_close(self):
        client.remove_listener(self.socket_listener)
        self.master.destroy()
        client.memory.tk_root.destroy()
    #listener
    def socket_listener(self, data):
        if data['type'] == util.message.MessageType.login_bundle:
            bundle = data['parameters']
            friends = bundle['friends']
            messages = bundle['messages']
            for friend in friends:
                self.handle_new_contact(friend)
            for item in messages:
                # [[data:bytes,sent:int]]
                sent = item[1]
                message = _deserialize_any(item[0])
                client.digest_message(message, not sent)

            self.bundle_process_done = True
            self.refresh_contacts()
        #加好友申请
        if data['type'] == util.message.MessageType.incoming_friend_request:
            result = messagebox.askyesnocancel("好友请求", data['parameters']['nickname'] + "请求加您为好友，是否同意？(按Cancel为下次再询问)");
            if result == None:
                return
            sendMessage(self.sc,util.message.MessageType.resolve_friend_request, [data['parameters']['id'], result])

        #通讯信息
        if data['type'] == util.message.MessageType.contact_info:
            self.handle_new_contact(data['parameters'])
            return
        #好友添加结果提示
        if data['type'] == util.message.MessageType.add_friend_result:
            if data['parameters'][0]:
                messagebox.showinfo('添加好友', '好友请求已发送')
            else:
                messagebox.showerror('添加好友失败', data['parameters'][1])
            return
        #好友离线，更新列表
        if data['type'] == util.message.MessageType.friend_on_off_line:
            friend_user_id = data['parameters'][1]
            for i in range(0, len(self.contacts)):
                if self.contacts[i]['id'] == friend_user_id and self.contacts[i]['type'] == 0:
                    self.contacts[i]['online'] = data['parameters'][0]
                    break

            self.refresh_contacts()
            return
    #新消息
    def handle_new_contact(self, data):
        data['last_timestamp'] = time.time()
        data['last_message'] = '(没有消息)'
        self.contacts.insert(0, data)
        self.refresh_contacts()
    #打开聊天窗口
    def on_frame_click(self, e):
        item_id = e.widget.item['id']
        if item_id in client.memory.window_instance[e.widget.item['type']]:
            client.memory.window_instance[e.widget.item['type']][item_id].master.deiconify()
            return
        form = Toplevel(client.memory.tk_root, takefocus=True)
        client.memory.window_instance[e.widget.item['type']][item_id] = ChatForm(e.widget.item, form)
    #添加朋友
    def on_add_friend(self):
        result = simpledialog.askstring('添加好友', '请输入用户名')
        if (not result):
            return
        sendMessage(self.sc, util.message.MessageType.add_friend, result)



    class my_event:
        widget = None
        def __init__(self, widget):
            self.widget = widget
    pack_objs = []
    # 切换至聊天记录
    def refresh_contacts(self):
        if not self.bundle_process_done:
            return
        for pack_obj in self.pack_objs:
            pack_obj.pack_forget()
            pack_obj.destroy()
            pack_obj.destroy()
        self.pack_objs = []
        self.contacts.sort(key=lambda x: -client.memory.last_message_timestamp[x['type']].get(x['id'], 0))
        for item in self.contacts:
            print(self.contacts)
            contact = Chat_record(self.scroll.interior, self.on_frame_click)
            contact.pack(fill=BOTH, expand=True)
            contact.item = item
            contact.bind("<Button>", self.on_frame_click)
            if (item['type'] == 0):
                contact.title.config(text=item['nickname'] + (' (在线)' if item['online'] else ' (离线)'))
                contact.title.config(fg='green' if item['online'] else '#999')
            self.pack_objs.append(contact)
            print('bug')
            end_time = 1525104000000
            time_message = datetime.datetime.fromtimestamp(
                item['last_timestamp']
                #end_time / 1000
            ).strftime('%Y-%m-%d %H:%M:%S')
            contact.last_message_time.config(text=time_message)
            contact.last_message.config(text=client.memory.last_message[item['type']].get(item['id'], '(没有消息)'))
            '''''
            contact.last_message_time.config(text=datetime.datetime.fromtimestamp(
                int(client.memory.last_message_timestamp[item['type']].get(item['id'], 0)) / 1000
            ).strftime('%Y-%m-%d %H:%M:%S'))
            '''''
            unread_count = client.memory.unread_message_count[item['type']].get(item['id'], 0)
            contact.unread_message_count.pack_forget()
            if unread_count != 0:
                contact.last_message.pack_forget()
                contact.unread_message_count.pack(side=RIGHT, anchor=E, fill=None, expand=False, ipadx=4)
                contact.last_message.pack(side=LEFT, fill=X, expand=True, anchor=W)
                contact.unread_message_count.config(text=str(unread_count))
    # 切换至通讯录
    def on_contact_list(self):
        if not self.bundle_process_done:
            return
        for pack_obj in self.pack_objs:
            pack_obj.pack_forget()
            pack_obj.destroy()
        self.pack_objs = []
        self.contacts = sorted(self.contacts, key=lambda x: ''.join(lazy_pinyin(x['nickname'])))
        for item in self.contacts:
            contact = Chat_member(self.scroll.interior, self.on_frame_click)
            contact.pack(fill=BOTH, expand=True)
            contact.item = item
            contact.bind("<Button>", self.on_frame_click)
            if (item['type'] == 0):
                contact.title.config(text=item['nickname'] + (' (在线)' if item['online'] else ' (离线)'))
                contact.title.config(fg='green' if item['online'] else '#999')
            self.pack_objs.append(contact)

    def __init__(self, master=None):
        client.memory.contact_window.append(self)
        super().__init__(master)
        self.master = master
        screen_width = client.memory.tk_root.winfo_screenwidth()
        screen_height = client.memory.tk_root.winfo_screenheight()
        x = screen_width - 300
        y = (screen_height / 2)-300
        master.geometry('%dx%d+%d+%d' % (260, 600, x, y))
        self.scroll = Chat_main(self)
        self.scroll.pack(fill=BOTH, expand=True)
        self.pack(side=TOP, fill=BOTH, expand=True)
        self.button_frame = Frame(self)
        self.contact_box = Button(self.button_frame, text="聊天记录", command=self.refresh_contacts)
        self.contact_box.pack(side=LEFT, expand=True, fill=X)
        self.contact_list = Button(self.button_frame, text="通讯录", command=self.on_contact_list)
        self.contact_list.pack(side=LEFT, expand=True, fill=X)
        self.add_friend = Button(self.button_frame, text="添加好友", command=self.on_add_friend)
        self.add_friend.pack(side=LEFT, expand=True, fill=X)
        self.button_frame.pack(expand=False, fill=X)
        self.contacts = []
        self.master.title(client.memory.current_user['nickname'] + " - 联系人列表")
        self.sc = client.memory.sc
        client.add_listener(self.socket_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_socket_listener_and_close)
