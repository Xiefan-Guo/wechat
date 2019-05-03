import util.message
from client.forms.register_form import RegisterForm
from client.forms.contacts_form import ContactsForm
from tkinter import *
import tkinter
import client
from tkinter import Toplevel
from util import send_message as sendMessage
from PIL import ImageTk, Image


class LoginForm(client.tk.Frame):
    #移除listener
    def remove_socket_listener_and_close(self):
        client.remove_listener(self.socket_listener)
        self.master.destroy()
    #关闭窗口
    def destroy_window(self):
        client.messagebox.showerror('网断了', '断了。。。')
        #client.memory.tk_root.destroy()

    #listener
    def socket_listener(self, data):
        if data['type'] == util.message.MessageType.login_failed:
            client.messagebox.showerror('登入失败', '登入失败，请检查用户名密码')
            return
        if data['type'] == util.message.MessageType.login_successful:
            client.memory.current_user = data['parameters']
            self.remove_socket_listener_and_close()
            contacts = Toplevel(client.memory.tk_root, takefocus=True)
            ContactsForm(contacts)
            return

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        master.resizable(width=False, height=False)

        self.master.geometry('300x120')

        self.master.iconbitmap('F:\pycharm_python\wechat\client\image\\wechat.ico')

        self.label_1 = Label(self, text="用户名")
        self.label_2 = Label(self, text="密码")
        self.username = Entry(self)
        self.password = Entry(self, show="*")
        self.label_1.grid(row=0, sticky=E)
        self.label_2.grid(row=1, sticky=E)
        self.username.grid(row=0, column=1, pady=(10, 6))
        self.password.grid(row=1, column=1, pady=(0, 6))
        self.buttonframe = Frame(self)
        self.buttonframe.grid(row=2, column=0, columnspan=2, pady=(4, 6))
        self.logbtn = Button(self.buttonframe, text="登入", bg='green', width=5, height=1, command=self.do_login)
        self.logbtn.grid(row=0, column=0)
        self.registerbtn = Button(self.buttonframe, text="注册", width=5, height=1,command=self.show_register)
        self.registerbtn.grid(row=0, column=1)

        self.pack()
        self.master.title("wechat")

        self.sc = client.memory.sc
        # self.sc.send(MessageType.client_echo, 0)
        client.add_listener(self.socket_listener)
    #进行登陆
    def do_login(self):
        username = self.username.get()
        password = self.password.get()
        if not username:
            client.messagebox.showerror("出错了", "用户名不能为空")
            return
        if not password:
            client.messagebox.showerror("出错了", "密码不能为空")
            return
        print()
        sendMessage(self.sc,util.message.MessageType.login, [username, password])
    #登陆成功
    def show_register(self):
        register_form = Toplevel()
        RegisterForm(register_form)
