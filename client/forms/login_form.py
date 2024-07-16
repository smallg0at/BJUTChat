#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""登录界面"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from common.message import MessageType

import client.memory
from client.forms.contacts_form import ContactsForm
from tkinter import *
from tkinter import Toplevel
import client.util.socket_listener
from common.config import get_config
import re
import logging
logger = logging.getLogger(__name__)

"""登录界面"""


class LoginForm(tk.Frame):
    """关闭端口监听"""

    def remove_socket_listener_and_close(self):
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()

    """" 关闭窗口 """

    def destroy_window(self):
        client.memory.tk_root.destroy()

    """ 开启监听 """

    def socket_listener(self, data):
        if data["type"] == MessageType.login_failed:
            messagebox.showerror("Error", "登入失败，请检查用户名密码")
            return

        if data["type"] == MessageType.login_successful:
            client.memory.current_user = data["parameters"]
            self.remove_socket_listener_and_close()
            logger.info("Login Successful!")
            contacts = Toplevel(client.memory.tk_root, takefocus=True)
            ContactsForm(contacts)
            return
    
        if data['type'] == MessageType.school_id_taken:
            messagebox.showerror('Error', '学工号已被使用，请联系管理员')
            return

        if data['type'] == MessageType.register_successful:
            messagebox.showinfo('Congratulations', '注册成功! ')
            # self.remove_socket_listener_and_close()
            return

    def __init__(self, master=None):
        """创建主窗口用来容纳其他组件"""
        super().__init__(master)
        # sv_ttk.set_theme('dark')
        
        
        self.master = master
        self.master.title("BJUTChat")
        # self.master.resizable(width=False, height=False)
        self.master.geometry("600x800")

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill='both')

        self.login_frame = ttk.Frame(self.notebook, width=600, height=800, style="White.TFrame")
        self.register_frame = ttk.Frame(self.notebook, width=600, height=800, style="White.TFrame")
        




        # Login
        # self.canvas = tk.Canvas(self.login_frame, width=600, height=400, background="#d9d9d9", highlightthickness=0)
        # 标签 用户名密码
        self.login_user_schoolid = ttk.Label(self.login_frame, text="学工号",justify='left', width=26,style="White.TLabel")
        self.login_user_pwd = ttk.Label(self.login_frame, text="密码",justify='left', width=26,style="White.TLabel")
        # 用户名输入框
        self.var_login_user_schoolid = tk.StringVar()
        self.login_entry_user_name = ttk.Entry(
            self.login_frame,
            textvariable=self.var_login_user_schoolid,
            font=("微软雅黑", 12),
            width=25,
            justify="center"
        )
        # 密码输入框
        self.login_var_user_pwd = tk.StringVar()
        self.login_entry_user_pwd = ttk.Entry(
            self.login_frame,
            textvariable=self.login_var_user_pwd,
            show="* ",
            font=("微软雅黑", 12),
            width=25,
            justify="center",
        )
        # 登录 注册按钮

        self.login_btn = ttk.Button(
            self.login_frame,
            text="登录",
            command=self.do_login,
            width=25,
            style="Accent.TButton",
        )
        self.version_label = ttk.Label(self.login_frame, text=f"BJUTChat {get_config()['version']}", style="White.TLabel", font=('微软雅黑', 9))

        # self.pack(expand=True, fill=BOTH)
        # 位置定位
        # self.canvas.grid(
        #     row=0,
        #     column=0,
        #     rowspan=6,
        #     columnspan=2,
        # )
        for i in range(0,6):
            self.login_frame.rowconfigure(i, weight=0, pad=15, minsize=20)
        

        self.login_frame.columnconfigure(0, weight=3)


        self.login_user_schoolid.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky=N,
            padx=0,
            pady=0,
        )
        self.login_entry_user_name.grid(row=2, column=0, columnspan=1, sticky=N)
        self.login_user_pwd.grid(row=3, column=0, columnspan=1, sticky=N)
        self.login_entry_user_pwd.grid(row=4, column=0, columnspan=1, sticky=N)
        self.login_btn.grid(row=6, column=0, columnspan=1, sticky=N)
        self.version_label.grid(row=7, column=0, sticky=N)
        # self.register_btn.grid(row=7, column=0, columnspan=2, sticky=N)
        # self.quit_btn.grid(row=8, column=0, columnspan=2, sticky=N)


        # Register
        # 画布
        # self.canvas = tk.Canvas(self.register_frame, width=600, height=1000, background="#d9d9d9", highlightthickness=0)
        # 标签 用户名、密码、确认密码、邮箱、性别、年龄
        self.reg_user_name = ttk.Label(self.register_frame, text="用户名 ",style="White.TLabel")
        self.reg_user_pwd = ttk.Label(self.register_frame, text="密码 ",style="White.TLabel")
        self.confirm_pwd = ttk.Label(self.register_frame, text="确认密码 ",style="White.TLabel")
        self.user_school_id = ttk.Label(self.register_frame, text="学工号 ",style="White.TLabel")
        self.user_sex = ttk.Label(self.register_frame, text="性别 ",style="White.TLabel")
        self.user_age = ttk.Label(self.register_frame, text="年龄 ",style="White.TLabel")
        self.user_role = ttk.Label(self.register_frame, text="角色 ",style="White.TLabel")
        # 输入框
        # 用户名输入框
        self.var_reg_user_name = tk.StringVar()
        self.reg_entry_user_name = ttk.Entry(self.register_frame, textvariable=self.var_reg_user_name, font=("微软雅黑", 12))
        # 密码输入框
        self.reg_var_user_pwd = tk.StringVar()
        self.reg_entry_user_pwd = ttk.Entry(self.register_frame, textvariable=self.reg_var_user_pwd, show='* ', font=("微软雅黑", 12))
        # 确认密码输入框
        self.var_confirm_pwd = tk.StringVar()
        self.entry_confirm_pwd = ttk.Entry(self.register_frame, textvariable=self.var_confirm_pwd, show='* ', font=("微软雅黑", 12))
        # 学/工号输入框
        self.var_user_school_id = tk.StringVar()
        self.entry_user_school_id = ttk.Entry(self.register_frame, textvariable=self.var_user_school_id,font=("微软雅黑", 12))
        # 性别输入框
        self.var_user_sex = tk.StringVar()
        self.entry_user_sex = ttk.Combobox(self.register_frame, textvariable=self.var_user_sex, font=("微软雅黑", 12),
                                           state="readonly")
        self.entry_user_sex['values'] = ("保密", "男", "女")
        self.entry_user_sex.current(0)

        # 角色输入框
        self.var_user_role = tk.StringVar()
        self.entry_user_role = ttk.Combobox(self.register_frame, textvariable=self.var_user_role, font=("微软雅黑", 12),
                                           state="readonly")
        self.entry_user_role['values'] = ("学生", "教师")
        self.entry_user_role.current("0")
        # 注册按钮
        self.register_btn = ttk.Button(self.register_frame, text='注册',
                                       width=25, style="Accent.TButton",
                                      command=self.do_register)
        # 位置定位
        # label位置定位
        # self.canvas.grid(row=0, column=0, rowspan=16, columnspan=8, )
        for i in range(0,8):
            self.register_frame.rowconfigure(i, weight=0, pad=15, minsize=20)
        
        
        self.register_frame.columnconfigure(0, weight=0, pad=15, minsize=20)
        self.register_frame.columnconfigure(1, weight=0, pad=15)
        self.register_frame.columnconfigure(2, weight=5, pad=15)
        self.register_frame.columnconfigure(3, weight=0, pad=15, minsize=20)
        
        
        self.reg_user_name.grid(row=1, column=1, sticky=E)
        self.reg_user_pwd.grid(row=2, column=1, sticky=E)
        self.confirm_pwd.grid(row=3, column=1, sticky=E)
        self.user_school_id.grid(row=4, column=1, sticky=E)
        self.user_sex.grid(row=5, column=1, sticky=E)
        self.user_role.grid(row=6, column=1, sticky=E)
        # 输入框位置定位
        self.reg_entry_user_name.grid(row=1, column=2, sticky='we', )
        self.reg_entry_user_pwd.grid(row=2, column=2, sticky='we', )
        self.entry_confirm_pwd.grid(row=3, column=2, sticky='we', )
        self.entry_user_school_id.grid(row=4, column=2, sticky='we', )
        self.entry_user_sex.grid(row=5, column=2, sticky='we', )
        self.entry_user_role.grid(row=6, column=2, sticky='we', )
        # 注册按钮位置定位
        self.register_btn.grid(row=7, column=1, columnspan=2, sticky=S)


        self.notebook.add(self.login_frame, text="登录")
        self.notebook.add(self.register_frame, text="注册")

        self.sc = client.memory.sc

        client.util.socket_listener.add_listener(self.socket_listener)

        self.master.protocol("WM_DELETE_WINDOW", self.destroy_window)

    """ 登陆操作 """

    def do_login(self):
        """登录操作若为空则提示用户错误"""
        schoolid = self.var_login_user_schoolid.get()
        password = self.login_var_user_pwd.get()
        if not schoolid:
            messagebox.showerror(
                "Error",
                "用户名不能为空",
            )
            return
        if not password:
            messagebox.showerror("Error", "密码不能为空")
            return
        self.sc.send(MessageType.login, [schoolid, password])


    """" 注册操作 """
    def do_register(self):

        username = self.var_reg_user_name.get()
        password = self.reg_var_user_pwd.get()
        password_confirmation = self.var_confirm_pwd.get()
        school_id = self.var_user_school_id.get()
        sex = self.var_user_sex.get()
        if self.entry_user_role.get() == "学生":
            role=0
        else:
            role=1
        config = get_config()
        port = str((config['client']['client_port']))

        if not username:
            messagebox.showerror("Error", "用户名不能为空")
            return
        if not school_id:
            messagebox.showerror("Error", "学/工号不能为空")
            return
        if not password:
            messagebox.showerror("Error", "密码不能为空")
            return
        if password != password_confirmation:
            messagebox.showerror("Error", "两次密码输入不一致")
            return
        # if not re.match(r'^[0-9]{0,8}$',school_id):
        #     messagebox.showerror("Error", "学工/号格式错误")
        #     return
        self.sc.send(MessageType.register, [username, password, school_id, sex, role])
