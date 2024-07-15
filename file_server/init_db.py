import sqlite3
import os
# 防呆设计
if not os.path.exists('file_server/database.db'):
    print("You're probably on the wrong working directory!")


# 连接到数据库
conn = sqlite3.connect('file_server/database.db')

if not os.path.exists('file_server'):
    os.makedirs('file_server')

# 创建一个游标对象
cur = conn.cursor()

# 删除现有的文件表（如果存在）
cur.execute('''DROP TABLE IF EXISTS "main"."files"''')
cur.execute('''DROP TABLE IF EXISTS "upload_logs"''')
cur.execute('''DROP TABLE IF EXISTS "download_logs"''')

# 创建一个名为files的表
cur.execute('''
CREATE TABLE "files" (
    "id" TEXT NOT NULL,
    "upload_time" INTEGER,
    "is_deleted" BOOLEAN,
    PRIMARY KEY ("id")
)
''')

cur.execute('''
CREATE TABLE "upload_logs" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "file_id" TEXT,
    "user_id" TEXT,
    "timestamp" INTEGER
)
''')

cur.execute('''
CREATE TABLE "download_logs" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "file_id" TEXT,
    "user_id" TEXT,
    "timestamp" INTEGER
)
''')

# 提交更改
conn.commit()

# 关闭连接
conn.close()