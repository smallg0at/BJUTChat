#!/usr/bin/env python
# -*- coding:utf-8 -*-

""""聊天界面及处理与聊天相关的事件"""
import tkinter as tk
from tkinter import *
from tkinter import ttk
import client.memory
from client.util.socket_listener import *
from tkinter.scrolledtext import ScrolledText
from tkinter import colorchooser
from tkinter import simpledialog
from tkinter import filedialog
from PIL import Image, ImageTk
from io import BytesIO
from client.util import socket_listener
import binascii
import time
import filetype
import os
from PIL import Image
import requests
from common.config import get_config
from tempfile import TemporaryFile
import base64
import threading
from client.components.HyperlinkManager import HyperlinkManager
from functools import partial
"""创建聊天框"""
class ChatForm(tk.Frame):

    font_color = "#000000"
    font_size = 16
    user_list = []
    tag_i = 0

    """将监听事件移除并关闭该窗口"""
    def remove_listener_and_close(self):
        remove_message_listener(self.message_listener)
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()
        if self.target['id'] in client.memory.window_instance[self.target['type']]:
            del client.memory.window_instance[self.target['type']][self.target['id']]

    """定义监听事件"""
    def message_listener(self, data):
        self.digest_message(data)

    """监听socket传来的数据"""
    def socket_listener(self, data):
        dirname = "send_msg_log"
        dir_flag = os.path.exists(dirname)
        if dir_flag == False:
            os.mkdir(dirname)
        # if data['parameters']['message']['type'] == 1:
        #     with open(dirname + '/' + filename, 'wb') as f:
        #         contents = data['parameters']['message']['data']
        #         f.write(contents)
        #         f.close()
        #     with open(dirname + '/' + filename, 'rb') as f:
        #         file_format = filetype.guess(dirname + '/' + filename)
        #         file_format = file_format.extension
        #         if file_format == None:
        #             file_format = "txt"
        #         f.close()
        #     os.rename(dirname + '/' + filename, (str(dirname + '/' + filename) + '_.' + file_format))
        if data['type'] == MessageType.query_room_users_result:
            if data['parameters'][1] != self.target['id']:
                return
            self.user_list = data['parameters'][0]
            self.refresh_user_listbox()
        if data['type'] == MessageType.room_user_on_off_line:
            if data['parameters'][0] != self.target['id']:
                return
            for i in range(0, len(self.user_list)):
                if self.user_list[i][0] == data['parameters'][1]:
                    self.user_list[i][2] = data['parameters'][2]
            self.refresh_user_listbox()

    """更新好友列表"""
    def refresh_user_listbox(self):
        self.user_listbox.delete(0, END)
        self.user_list.sort(key=lambda x: x[2])
        for user in self.user_list:
            self.user_listbox.insert(0, user[1] + ("(在线)" if user[2] else "(离线)"))
            self.user_listbox.itemconfig(0, {'fg': ("blue" if user[2] else "#505050")})

    """处理消息并将其展示出来"""
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
                                     lmargin2=16)
            self.append_to_chat_box(data['message']['data'] + '\n',
                                    'new' + str(self.tag_i))
        if data['message']['type'] == 1:
            client.memory.tk_img_ref.append(ImageTk.PhotoImage(data=base64.b64decode(data['message']['data'])))
            image_index = self.chat_box.image_create(END, image=client.memory.tk_img_ref[-1], padx=16, pady=5)
            threading.Thread(target=self.load_full_size_image, args=(image_index, data['message']['uuid'])).start()
            self.append_to_chat_box('\n', '')
            self.chat_box.insert(END, "另存为\n", self.hyperlink_mgr.add(partial(self.save_specific_image, data['message']['uuid'], data['message']['basename'])))
        if data['message']['type'] == 1:
            self.chat_box.insert(END, f"【文件】{data['message']['basename']}\n", self.hyperlink_mgr.add(partial(self.save_specific_image, data['message']['uuid'], data['message']['basename'])))

    def load_full_size_image(self, index, file_id):
        # Get the full-sized image URL from data['message']['data']
        server_url = get_config()['file_server']

        if(os.path.exists(f"userdata/image_attachments/{file_id}")):
            full_size_image = self.shrink_image_by_ratio(Image.open(f"userdata/image_attachments/{file_id}"))
            shrunk_image = ImageTk.PhotoImage(self.shrink_image_by_ratio(full_size_image))
            client.memory.tk_img_ref.append(shrunk_image)
            self.chat_box.image_configure(index, image=client.memory.tk_img_ref[-1], padx=16, pady=5)
        else: 
            params1 = {'user_id': client.memory.current_user['id'], 'file_id': file_id}
            response = requests.get(f'{server_url}/download', params=params1)

            if response.status_code == 200:
                # Load the full-sized image using Pillow or other image library
                with open(file=f"userdata/image_attachments/{file_id}", mode='wb') as f:
                    f.write(response.content)
                    f.close()
                full_size_image = ImageTk.PhotoImage(self.shrink_image_by_ratio(Image.open(f"userdata/image_attachments/{file_id}")))
                client.memory.tk_img_ref.append(full_size_image)
                print(len(response.content))
                if(not os.path.exists(f"userdata/image_attachments")):
                    os.makedirs(f"userdata/image_attachments")
                # self.chat_box.image_create(index, image=None)
                            # self.chat_box.image_create(index, image=None)
                self.chat_box.image_configure(index, image=client.memory.tk_img_ref[-1], padx=16, pady=5)

                print("success")

            else:
                print("Error loading full-sized image")
                self.append_to_chat_box('\n', '')

    def shrink_image_by_ratio(self, image, longest=1600):
        height = image.height
        width = image.width
        if height > width:
            if height > longest:
                # print((int(longest*width/height), longest))
                return image.resize((int(longest*width/height), longest))
            else:
                return image
        else: 
            if width > longest:
                # print(longest, int(longest*height/width))
                return image.resize((longest, int(longest*height/width)))
            else:
                return image

    def save_specific_image(self, uuid, defaultname):
        if not os.path.exists(f"userdata/image_attachments/{uuid}"):
            messagebox.showerror("错误", "图片未能成功获取，无法保存")
            return
        with filedialog.asksaveasfile(mode="wb", title="保存图片", initialfile=defaultname) as f:
            with open(f"userdata/image_attachments/{uuid}", 'rb') as ffrom:
                f.write(ffrom.read())
                f.close()
                ffrom.close()

    def save_specific_file(self, uuid, defaultname):
        pass

    """ 双击聊天框 """
    def user_listbox_double_click(self, _):
        if len(self.user_listbox.curselection()) == 0:
            return None
        index = self.user_listbox.curselection()[0]
        selected_user_id = self.user_list[len(self.user_list) - 1 - index][0]
        selected_user_username = self.user_list[len(self.user_list) - 1 - index][3]
        if selected_user_id == client.memory.current_user['id']:
            return
        client.memory.contact_window[0].try_open_user_id(selected_user_id,
                                                         selected_user_username)
        return

    def __init__(self, target, master=None):
        super().__init__(master)
        self.master = master
        self.target = target
        self.user_listbox = tk.Listbox(self, width=0, bd=0)
        client.util.socket_listener.add_listener(self.socket_listener)
        client.memory.unread_message_count[self.target['type']][self.target['id']] = 0
        client.memory.contact_window[0].refresh_contacts()
        master.resizable(width=True, height=True)
        master.geometry('1160x1000')
        self.sc = client.memory.sc
        # 私人聊天
        if self.target['type'] == 0:
            self.master.title(self.target['username'])
        # 群组聊天
        if self.target['type'] == 1:
            self.master.title("[群:" + str(self.target['id']) + "] " + self.target['room_name'])
            self.sc.send(MessageType.query_room_users, self.target['id'])

        self.right_frame = tk.Frame(self)

        self.user_listbox.bind('<Double-Button-1>', self.user_listbox_double_click)
        if self.target['type'] == 1:
            self.user_listbox.pack(side=LEFT, expand=False, fill=BOTH)

        self.right_frame.pack(side=LEFT, expand=True, fill=BOTH)
        self.input_frame = tk.Frame(self.right_frame)
        self.input_textbox = ScrolledText(self.right_frame, font=("微软雅黑", 16), height=5, background="#f0f0f0")
        self.input_textbox.bind("<Control-Return>", self.send_message)
        self.input_textbox.bind_all('<Key>', self.apply_font_change)
        self.send_btn = ttk.Button(self.input_frame, text='发送消息', command=self.send_message)
        self.send_btn.pack(side=RIGHT, expand=False)
        # self.font_btn = tk.Button(self.input_frame, text='字体颜色', font=("微软雅黑", 16, 'bold'), fg="black", relief=GROOVE, command=self.choose_color)
        # self.font_btn.pack(side=LEFT, expand=False)
        # self.font_btn = tk.Button(self.input_frame, text='字体大小', font=("微软雅黑", 16, 'bold'), fg="black", relief=GROOVE, command=self.choose_font_size)
        # self.font_btn.pack(side=LEFT, expand=False)
        self.image_btn = ttk.Button(self.input_frame, text='发送图片', command=self.send_image)
        self.image_btn.pack(side=LEFT, expand=False)
        self.chat_box = ScrolledText(self.right_frame)
        self.input_frame.pack(side=BOTTOM, fill=X, expand=False)
        self.input_textbox.pack(side=BOTTOM, fill=X, expand=False, padx=(0, 0), pady=(0, 0))
        self.chat_box.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.chat_box.bind("<Key>", lambda e: "break")
        self.hyperlink_mgr = HyperlinkManager(self.chat_box)
        self.chat_box.tag_config("default", lmargin1=10, lmargin2=10, rmargin=10, font=("微软雅黑", 15))
        self.chat_box.tag_config("me", foreground="green", spacing1='0', font=("微软雅黑", 12))
        self.chat_box.tag_config("them", foreground="blue", spacing1='0', font=("微软雅黑", 12))
        self.chat_box.tag_config("message", foreground="black", spacing1='0', font=("微软雅黑", 15))
        self.chat_box.tag_config("system", foreground="#505050", spacing1='0', justify='center', font=("微软雅黑", 10))

        self.pack(expand=True, fill=BOTH)

        add_message_listener(self.target['type'], self.target['id'], self.message_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_listener_and_close)

        # 历史消息显示
        if target['id'] in client.memory.chat_history[self.target['type']]:
            for msg in client.memory.chat_history[self.target['type']][target['id']]:
                self.digest_message(msg)

            self.append_to_chat_box('- 以上是历史消息 -\n', 'system')

    """ 附加聊天框 """
    def append_to_chat_box(self, message, tags):
        self.chat_box.insert(tk.END, message, [tags, 'default'])
        self.chat_box.update()
        self.chat_box.see(tk.END)

    """ 发送消息 """
    def send_message(self, _=None):
        message = self.input_textbox.get("1.0", END)
        if not message or message.replace(" ", "").replace("\r", "").replace("\n", "") == '':
            return
        self.sc.send(MessageType.send_message,
                     {'target_type': self.target['type'], 'target_id': self.target['id'],
                      'message': {
                          'type': 0,
                          'data': message.strip().strip('\n'),
                      }
                      })
        self.input_textbox.delete("1.0", END)
        return 'break'

    """ 选择字体颜色 """
    def choose_color(self):
        _, self.font_color = colorchooser.askcolor(initialcolor=self.font_color)
        self.apply_font_change(None)

    """ 选择字体大小 """
    def choose_font_size(self):
        result = simpledialog.askinteger("设置", "请输入字体大小", initialvalue=self.font_size)
        if result is None:
            return
        self.font_size = result
        self.apply_font_change(None)

    """" 更新字体 """
    def apply_font_change(self, _):
        try:
            self.input_textbox.tag_config('new', foreground=self.font_color, font=(None, self.font_size))
            self.input_textbox.tag_add('new', '1.0', END)
        except:
            pass

    """" 发送图片 """
    def send_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image Files",
                                                          ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.JPG", "*.JPEG",
                                                           "*.PNG", "*.GIF"]),
                                                         ("All Files", ["*.*"])])
        
        if filename is None or filename == '':
            return
        basename = os.path.basename(filename)
        image = Image.open(filename)
        small_image = image.resize((128,128))
        fp = TemporaryFile()
        small_image.save(fp, 'PNG')
        fp.seek(0)
        with open(filename, "rb") as imageFile:
            files = {'file': imageFile}
            data = {'user_id': client.memory.current_user['id']}
            server_url = get_config()['file_server']
            response = requests.post(f'{server_url}/upload', files=files, data=data)
            if(response.status_code == 200):
                file_id = response.json().get('file_id')

                f = fp.read()
                b = base64.b64encode(f).decode('ascii')
                print("Sendsize", len(b))
                self.sc.send(MessageType.send_message,
                             {'target_type': self.target['type'], 'target_id': self.target['id'],
                              'message': {'type': 1, 'data': b, 'uuid': file_id, 'basename': basename}})
                print('send image success!')
                messagebox.showinfo("提示", "图片发送成功")
            else:
                messagebox.showerror("提示", f"图片发送失败。错误码：{response.status_code}")
    def send_file(self):
        filename = filedialog.askopenfilename()
        
        if filename is None or filename == '':
            return
        basename = os.path.basename(filename)
        with open(filename, "rb") as imageFile:
            files = {'file': imageFile}
            data = {'user_id': client.memory.current_user['id']}
            server_url = get_config()['file_server']
            response = requests.post(f'{server_url}/upload', files=files, data=data)
            if(response.status_code == 200):
                file_id = response.json().get('file_id')
                self.sc.send(MessageType.send_message,
                             {'target_type': self.target['type'], 'target_id': self.target['id'],
                              'message': {'type': 2, 'uuid': file_id, 'basename': basename}})
                print('send file success!')
                messagebox.showinfo("提示", "文件发送成功")
            else:
                messagebox.showerror("提示", f"文件发送失败。错误码：{response.status_code}")
