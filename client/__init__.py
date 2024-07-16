#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""运行客户端"""
import _thread
import tkinter as tk
from tkinter import ttk
import sv_ttk
import ctypes
from tkinter import messagebox
import client.memory
import client.util.socket_listener
from client.forms.login_form import LoginForm
from common.transmission.secure_channel import establish_secure_channel_to_server
import logging
import platform
logger = logging.getLogger(__name__)

"""运行客户端开启一个新的线程"""
def run():
    
    root = tk.Tk()
    client.memory.tk_root = root
    ScaleFactor = 72
    if platform.system() == 'Windows': 
        # 告诉操作系统使用程序自身的dpi适配
        try:  # >= win 8.1
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:  # win 8.0 or less
            ctypes.windll.user32.SetProcessDPIAware()
        #获取屏幕的缩放因子
        ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
        # 设置程序缩放
        client.memory.tk_root.tk.call('tk', 'scaling', ScaleFactor/72)
    else:
        # 获取屏幕尺寸
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # 获取屏幕物理尺寸（毫米）
        screen_mm_width = root.winfo_screenmmwidth()
        screen_mm_height = root.winfo_screenmmheight()

        # 计算DPI
        dpi_x = screen_width / (screen_mm_width / 25.4)
        dpi_y = screen_height / (screen_mm_height / 25.4)
        client.memory.tk_root.tk.call('tk', 'scaling', ScaleFactor/72)

    sv_ttk.set_theme('light')
    logging.info(ScaleFactor)
    style = ttk.Style()
    style.configure(".", font=("微软雅黑", 12))
    style.configure("Contact.TSeparator", background="#000000")
    style.configure("Contact.TFrame", background="#f0f0f0") 
    style.configure("White.TFrame", background="#fafafa") 
    style.configure("White.TLabel", background="#fafafa") 
    style.configure("Contact1.TFrame", background="#f0f0f0")
    logging.basicConfig(filename='./client.log', level=logging.INFO)
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