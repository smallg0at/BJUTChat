import tkinter as tk
from tkinter import scrolledtext
import datetime, time
class AnnouncementApp:
    def __init__(self, root, announcements = [
            {"title": "Announcement 1", "content": "Content of announcement 1", "send_time": "2024-07-12 10:00 AM"},
            {"title": "Announcement 2", "content": "Content of announcement 2", "send_time": "2024-07-12 11:00 AM"},
            {"title": "Announcement 3", "content": "Content of announcement 3", "send_time": "2024-07-12 12:00 PM"},
        ]
):
        self.root = root
        self.root.title("Announcement List")
        root.geometry('800x1280')
        # Set up the ScrolledText widget
        self.scroll_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=20, highlightthickness=0, relief='flat')
        self.scroll_text.pack(padx=10, pady=10, expand=True, fill='both')
        self.scroll_text.tag_config("title", font=("微软雅黑", 15, 'bold'))
        self.scroll_text.tag_config("time", font=("微软雅黑", 9), foreground="#666666")
        self.scroll_text.tag_config("content", font=("微软雅黑", 12))

        # Display the announcements
        for announcement in announcements:
            self.display_announcement(announcement)

    def display_announcement(self, announcement):
        timestr = datetime.datetime.fromtimestamp(
            int(announcement['send_time'])
        ).strftime('%Y-%m-%d %H:%M')
        self.scroll_text.insert(tk.END, f"» {announcement['title']}\n", 'title')
        self.scroll_text.insert(tk.END, f"{timestr}\n", 'time')
        self.scroll_text.insert(tk.END, f"{announcement['content']}\n", 'content')
        self.scroll_text.insert(tk.END, "\n\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnnouncementApp(root)
    root.mainloop()
