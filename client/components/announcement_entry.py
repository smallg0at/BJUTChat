#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""联系人列表 UI"""
from tkinter import *
from tkinter import ttk
from common.util import resourcePath
""""联系人界面"""
class AnnouncementEntry(Frame):

    def __init__(self, parent, onclick):
        Frame.__init__(self, parent)

        # style = ttk.Style()
        # style.configure("TAnnounTitle", font=("微软雅黑", 14, 'bold'))
        

        def handle_on_click(e):
            e.widget = self
            onclick(e)

        Frame.config(self, borderwidth=2, relief=FLAT, background="#ffffff")
        self.divider = ttk.Separator(self, orient='vertical')
        self.divider.pack(side='left', fill='y')
        self.menuicn = PhotoImage(file = resourcePath("./client/forms/assets/announce.png")).subsample(32)
        self.announce_content = ttk.Label(self,image=self.menuicn, text=f" 暂无公告", compound=LEFT, justify='left', background="#ffffff", font=("微软雅黑", 10), foreground="#a0a0a0")
        self.announce_content.pack(side='left', fill='none', pady=10)
        self.announce_content.bind('<Button>', handle_on_click)
        self.bind('<Button>', handle_on_click)

        self.pack()

        return
