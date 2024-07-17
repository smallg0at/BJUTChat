#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""联系人列表"""
import _tkinter
import tkinter as tk
from tkinter import ttk
from distutils import command
from tkinter import messagebox
from common.message import MessageType, _deserialize_any

import client.memory
from tkinter import *
from client.components.vertical_scrolled_frame import VerticalScrolledFrame
from client.components.contact_item import ContactItem
from client.forms.chat_form import ChatForm
from tkinter import Toplevel
import datetime
import client.util.socket_listener
import client.components.simpledialog as simpledialog
import orjson
from client.components.announcement_entry import AnnouncementEntry
from client.forms.announcements_form import AnnouncementApp
from client.components.HyperlinkManager import HyperlinkManager
from common.util import resourcePath
import logging
logger = logging.getLogger(__name__)
class ContactsForm(tk.Frame):
    bundle_process_done = False

    """#关闭contacts_form"""
    def remove_socket_listener_and_close(self):
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()
        client.memory.tk_root.destroy()

    """监听从服务端发来的反馈"""
    def socket_listener(self, data):
        logger.debug("Something happened...", data['type'])
        if data['type'] == MessageType.login_bundle:
            logger.info("Got Loginbundle! Length is %s", len(data))
            bundle = data['parameters']
            friends = bundle['friends']
            rooms = bundle['rooms']
            messages = bundle['messages']
            for friend in friends:
                self.handle_new_contact(friend)
            for room in rooms:
                self.handle_new_contact(room)
            for item in messages:
                sent = item[1]
                message = orjson.loads(item[0])
                client.util.socket_listener.digest_message(message, not sent)
            self.handle_announcements(bundle['announcements'])
            self.bundle_process_done = True
            self.refresh_contacts()

        if data['type'] == MessageType.incoming_friend_request:
            result = messagebox.askyesnocancel("好友请求", data['parameters']['username'] + "请求加您为好友，是否同意？(按取消为下次再询问)");
            if result == None:
                return
            self.sc.send(MessageType.resolve_friend_request, [data['parameters']['id'], result])

        if data['type'] == MessageType.contact_info:
            self.handle_new_contact(data['parameters'])
            return

        if data['type'] == MessageType.del_info:
            self.handle_del_contact(data['parameters'])
            return
        if data['type'] == MessageType.del_info_group:
            self.handle_del_group(data['parameters'])
            return

        if data['type'] == MessageType.add_friend_result:
            if data['parameters'][0]:
                if data['parameters'][1] == 'force':
                    messagebox.showinfo('添加好友', '好友已加')
                else:
                    messagebox.showinfo('添加好友', '好友请求已发送')
            else:
                messagebox.showerror('添加好友失败', data['parameters'][1])
            return

        if data['type'] == MessageType.del_friend_result:
            if data['parameters'][0]:
                messagebox.showinfo('删除好友', '成功删除好友')
            else:
                messagebox.showerror('删除好友失败', data['parameters'][1])
            return


    """处理新的联系人"""
    def handle_new_contact(self, data):
        data['last_timestamp'] = 0
        data['last_message'] = '(没有消息)'
        self.contacts.insert(0, data)
        logger.debug("Now has contact count: ", len(self.contacts))
        self.refresh_contacts()

    """处理删除好友的操作后"""
    def handle_del_contact(self, data):
        id = data['id']
        for conn in self.contacts:
            if (conn['id'] == id and conn['type'] == 0):
                self.contacts.remove(conn)
        self.refresh_contacts()
    """处理删除好友的操作后"""
    def handle_del_group(self, data):
        id = data['id']
        for conn in self.contacts:
            if (conn['id'] == id and conn['type'] == 1):
                self.contacts.remove(conn)
        self.refresh_contacts()

    def handle_announcements(self, data):
        if len(data) == 0:
            return
        self.announcement_entry.announce_content.config(text=f' {data[0]["title"]}')
        self.announcement_list = data

    def on_frame_click(self, e):
        item_id = e.widget.item['id']
        if item_id in client.memory.window_instance[e.widget.item['type']]:
            client.memory.window_instance[e.widget.item['type']][item_id].master.deiconify()
            return
        form = Toplevel(client.memory.tk_root, takefocus=True)
        client.memory.window_instance[e.widget.item['type']][item_id] = ChatForm(e.widget.item, form)

    def on_ann_click(self, e):
        form = Toplevel(client.memory.tk_root, takefocus=True)
        AnnouncementApp(form, self.announcement_list)


    """ 添加好友 """
    def on_add_friend(self):
        result = simpledialog.askstring('添加好友', '请输入学工号')
        if (not result):
            return
        self.sc.send(MessageType.add_friend, result)

    """ 删除好友 """
    def on_del_friend(self):
        result = simpledialog.askstring('删除好友', '请输入学工号')
        if (not result):
            return
        self.sc.send(MessageType.del_friend, result)

    """ 查看用户信息 """
    def on_user_information(self):
        return

    """ 添加群 """
    def on_add_room(self):
        result = simpledialog.askinteger('添加群', '请输入群号')
        if (not result):
            return
        self.sc.send(MessageType.join_room, result)

    """" 创建群 """
    def on_create_room(self):
        result = simpledialog.askstring('创建群', '请输入群名称')
        if (not result):
            return
        self.sc.send(MessageType.create_room, result)

    def on_alter_username(self):
        result = simpledialog.askstring('更改用户名', '请输入新用户名')
        if (not result):
            return
        self.sc.send(MessageType.alter_username, {'new_username': result})
    class my_event:
        widget = None
        def __init__(self, widget):
            self.widget = widget

    """ 查看用户ID """
    def try_open_user_id(self, id, username):
        for i in range(0, len(self.pack_objs)):
            frame = self.pack_objs[i]
            if frame.item['id'] == id and frame.item['type'] == 0:
                self.on_frame_click(self.my_event(frame))
                return
        result = messagebox.askyesno("是否加好友", username + "不在您的好友列表中，是否加好友？")
        if result:
            self.sc.send(MessageType.add_friend, username)
    pack_objs = []

    """更新列表界面"""
    def refresh_contacts(self):
        if not self.bundle_process_done:
            return

        def compare(item1, item2):
            ts1 = client.memory.last_message_timestamp[item1['type']].get(item1['id'], 0)
            ts2 = client.memory.last_message_timestamp[item2['type']].get(item2['id'], 0)
            if ts1 < ts2:
                return -1
            elif ts1 > ts2:
                return 1
            else:
                return 0

        for pack_obj in self.pack_objs:
            pack_obj.pack_forget()
            pack_obj.destroy()


        self.pack_objs = []
        self.contacts.sort(key=lambda x: -client.memory.last_message_timestamp[x['type']].get(x['id'], 0))

        for item in self.contacts:
            contact = ContactItem(self.scroll.interior, self.on_frame_click)
            contact.pack(fill=BOTH, expand=True)
            contact.item = item
            
            contact.bind("<Button>", self.on_frame_click)
            if (item['type'] == 0):
                # 联系人
                contact.title.config(text=f"{item['username']} ({item['school_id']})")
                contact.title.config(fg='#000000')
            if (item['type'] == 1):
                # 群
                contact.title.config(text=f'[群] {item["room_name"]} ({str(item["id"])})')
                contact.title.config(fg='green')

            self.pack_objs.append(contact)
            time_message = datetime.datetime.fromtimestamp(
                item['last_timestamp']
            ).strftime('%Y-%m-%d %H:%M')

            contact.last_message_time.config(text=time_message)

            contact.last_message.config(text=client.memory.last_message[item['type']].get(item['id'], '(没有消息)'))
            contact.last_message_time.config(text=datetime.datetime.fromtimestamp(
                int(client.memory.last_message_timestamp[item['type']].get(item['id'], 0)) / 1000
            ).strftime('%Y-%m-%d %H:%M'))

            unread_count = client.memory.unread_message_count[item['type']].get(item['id'], 0)
            contact.unread_message_count.pack_forget()
            if unread_count != 0:
                contact.last_message.pack_forget()
                contact.unread_message_count.pack(side=RIGHT, anchor=E, fill=None, expand=False, ipadx=4)
                contact.last_message.pack(side=LEFT, fill=X, expand=True, anchor=W)
                contact.unread_message_count.config(text=str(unread_count))

    

    def __init__(self, master=None):
        client.memory.contact_window.append(self)
        super().__init__(master)
        master.option_add('*tearOff', FALSE)
        self.master = master
        self.master.title(f"{client.memory.current_user['username']} ({client.memory.current_user['school_id']}) - 联系人")
        # master.resizable(width=False, height=False)
        master.geometry('800x1280')

        self.top_layout = Frame(self, relief='flat')
        self.top_layout.pack(side=TOP, fill='both')
        self.menuicn = PhotoImage(file = resourcePath("./client/forms/assets/globnav.png")).subsample(18) 
        self.menu_btn = ttk.Menubutton(self.top_layout, image=self.menuicn, text=" 菜单", compound=LEFT, width=5)
        self.menu = Menu(self.menu_btn, font=("微软雅黑", 12), background="#ffffff", relief=FLAT)
        self.menu_btn['menu'] = self.menu
        self.menu.add
        self.menu.add_command(label="添加好友", command=self.on_add_friend)
        self.menu.add_command(label="删除好友", command=self.on_del_friend)
        self.menu.add_separator()
        self.menu.add_command(label="新建群聊", command=self.on_create_room)
        self.menu.add_command(label="加入群聊", command=self.on_add_room)
        self.menu.add_separator()
        self.menu.add_command(label="更改用户名", command=self.on_alter_username)
        self.menu.add_command(label="退出", command=self.remove_socket_listener_and_close)



        self.menu_btn.pack(side=LEFT)
        
        self.announcement_entry = AnnouncementEntry(self.top_layout, self.on_ann_click)
        self.announcement_entry.pack(side=TOP, fill=BOTH, expand=True)
        self.announcement_list = []
        # 滚动条＋消息列表画布
        self.scroll = VerticalScrolledFrame(self, bg="#d9d9d9")
        self.scroll.pack(side=TOP, fill=BOTH, expand=True)
        # # 按钮
        # self.button_frame_left = Frame(self)
        # self.button_frame_left.pack(side=LEFT, fill=BOTH, expand=YES)
        # self.button_frame_right = Frame(self)
        # self.button_frame_right.pack(side=RIGHT, fill=BOTH, expand=YES)
        # # 添加好友
        # self.add_friend = ttk.Button(self.button_frame_left, text="添加好友",  command=self.on_add_friend)
        # self.add_friend.pack(side=TOP, expand=True, fill=BOTH)
        # # 添加群聊
        # self.add_room = ttk.Button(self.button_frame_left, text="添加群聊",  command=self.on_add_room)
        # self.add_room.pack(side=TOP, expand=True, fill=BOTH)
        # # 删除好友
        # self.del_friend = ttk.Button(self.button_frame_right, text="删除好友",  command=self.on_del_friend)
        # self.del_friend.pack(side=TOP, expand=True, fill=BOTH)
        # # 创建群聊
        # self.create_room = ttk.Button(self.button_frame_right, text="创建群聊",  command=self.on_create_room)
        # self.create_room.pack(side=TOP, expand=True, fill=BOTH)
        # 页面定位
        self.pack(side=TOP, fill=BOTH, expand=True)
        self.contacts = []
        self.sc = client.memory.sc
        client.util.socket_listener.add_listener(self.socket_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_socket_listener_and_close)