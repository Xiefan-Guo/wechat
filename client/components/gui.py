from tkinter import *

#聊天记录界面列表
class Chat_record(Frame):
    def __init__(self, parent, onclick):
        Frame.__init__(self, parent)
        def handle_on_click(e):
            e.widget = self
            onclick(e)
        Frame.config(self, background='white', borderwidth=2, relief=GROOVE)
        self.title_frame = Frame(self, bg='white')
        self.title_frame.pack(side=TOP, fill=X, expand=True, anchor=W, pady=(1, 1), padx=3)
        self.title = Label(self.title_frame, text="Title", bg='white')
        self.title.pack(side=LEFT, fill=None, anchor=W)
        self.last_message_time = Label(self.title_frame, text="date", font=('', 8), fg='#999', bg='white')
        self.last_message_time.pack(side=RIGHT, anchor=E)
        self.message_frame = Frame(self, bg='white')
        self.message_frame.pack(side=TOP, fill=X, expand=True, anchor=W, pady=(0, 5), padx=3)
        self.unread_message_count = Label(self.message_frame, text="0", font=('', 9), fg='white', bg='red')
        self.unread_message_count.pack(side=RIGHT, anchor=E, fill=None, expand=False, ipadx=4)
        self.unread_message_count.pack_forget()
        self.last_message = Label(self.message_frame, text="recent message", font=('', 9), fg='#666', bg='white')
        self.last_message.pack(side=LEFT, fill=X, expand=True, anchor=W)
        self.title.bind("<Button>", handle_on_click)
        self.last_message_time.bind("<Button>", handle_on_click)
        self.last_message.bind("<Button>", handle_on_click)
        self.unread_message_count.bind("<Button>", handle_on_click)
        self.message_frame.bind("<Button>", handle_on_click)
        self.title_frame.bind("<Button>", handle_on_click)
        self.pack()
        return
#通讯录界面列表
class Chat_member(Frame):
    def __init__(self, parent, onclick):
        Frame.__init__(self, parent)
        def handle_on_click(e):
            e.widget = self
            onclick(e)
        Frame.config(self, background='white', borderwidth=2, relief=GROOVE)
        self.title_frame = Frame(self, bg='white')
        self.title_frame.pack(side=TOP, fill=X, expand=True, anchor=W, pady=(1, 1), padx=3)
        self.title = Label(self.title_frame, text="Title", bg='white')
        self.title.pack(side=LEFT, fill=None, anchor=W)
        self.title.bind("<Button>", handle_on_click)
        self.title_frame.bind("<Button>", handle_on_click)
        self.pack()
        return
#主要垂直框架
class Chat_main(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)
        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        return