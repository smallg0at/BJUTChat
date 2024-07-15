#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""运行客户端"""
import _thread
import tkinter as tk
import sv_ttk
import ctypes
from tkinter import messagebox
import client.memory
import client.util.socket_listener
from client.forms.login_form import LoginForm
from common.transmission.secure_channel import establish_secure_channel_to_server

"""运行客户端开启一个新的线程"""
def run():
    
    root = tk.Tk()
    client.memory.tk_root = root
    # 告诉操作系统使用程序自身的dpi适配
    try:  # >= win 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:  # win 8.0 or less
        ctypes.windll.user32.SetProcessDPIAware()
    #获取屏幕的缩放因子
    ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
    # 设置程序缩放
    client.memory.tk_root.tk.call('tk', 'scaling', ScaleFactor/75)
    
    sv_ttk.set_theme('light')
    
    try:
        client.memory.sc = establish_secure_channel_to_server()
    except ConnectionError:
        messagebox.showerror("出错了", "无法连接到服务器")
        exit(1)

    _thread.start_new_thread(client.util.socket_listener.socket_listener_thread, (client.memory.sc, root))
    login = tk.Toplevel()
    
    LoginForm(master=login)
    root.withdraw()
    
    root.mainloop()
    try:
        root.destroy()
    except tk.TclError:
        pass