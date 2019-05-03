import tkinter as tk
from tkinter import messagebox
import util.message
import client.memory
import client
from tkinter import *
from util import send_message as sendMessage


class RegisterForm(tk.Frame):
    #listener
    def socket_listener(self, data):
        if data['type'] == util.message.MessageType.username_taken:
            messagebox.showerror('出错了', '用户名已被使用，请换一个')
            return
        if data['type'] == util.message.MessageType.register_successful:
            messagebox.showinfo('恭喜', '恭喜，注册成功，您的用户ID为：' + str(data['parameters']))
            self.remove_socket_listener_and_close()
            return
    #移除listener
    def remove_socket_listener_and_close(self):
        client.remove_listener(self.socket_listener)
        self.master.destroy()
    #进行注册
    def do_register(self):
        username = self.username.get()
        password = self.password.get()
        password_confirmation = self.password_confirmation.get()
        nickname = self.nickname.get()
        if not username:
            messagebox.showerror("出错了", "用户名不能为空")
            return
        if not password:
            messagebox.showerror("出错了", "密码不能为空")
            return
        if not nickname:
            messagebox.showerror("出错了", "昵称不能为空")
            return
        if password != password_confirmation:
            messagebox.showerror("出错了", "两次密码输入不一致")
            return
        sendMessage(self.sc, util.message.MessageType.register, [username, password, nickname])
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.sc = client.memory.sc
        master.resizable(width=False, height=False)
        master.geometry('260x160')
        self.master.iconbitmap('F:\pycharm_python\wechat\client\image\\wechat.ico')
        self.master.title("注册账户")
        self.label_1 = Label(self, text="用户名")
        self.label_2 = Label(self, text="密码")
        self.label_3 = Label(self, text="确认密码")
        self.label_4 = Label(self, text="昵称")
        self.username = Entry(self)
        self.password = Entry(self, show="*")
        self.password_confirmation = Entry(self, show="*")
        self.nickname = Entry(self)
        self.label_1.grid(row=0, sticky=E)
        self.label_2.grid(row=1, sticky=E)
        self.label_3.grid(row=2, sticky=E)
        self.label_4.grid(row=3, sticky=E)
        self.username.grid(row=0, column=1, pady=(10, 6))
        self.password.grid(row=1, column=1, pady=(0, 6))
        self.password_confirmation.grid(row=2, column=1, pady=(0, 6))
        self.nickname.grid(row=3, column=1, pady=(0, 6))
        self.regbtn = Button(self, text="注册", bg='green',width=6, height=1, command=self.do_register)
        self.regbtn.grid(row=4, column=0, columnspan=2)
        self.pack()
        self.sc = client.memory.sc
        client.add_listener(self.socket_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_socket_listener_and_close)
