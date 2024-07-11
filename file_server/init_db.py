import sqlite3

# 连接到数据库
conn = sqlite3.connect('server/database.db')

# 创建一个游标对象
cur = conn.cursor()

# 删除现有的文件表（如果存在）
cur.execute('''DROP TABLE IF EXISTS "main"."files"''')

# 创建一个名为files的表
cur.execute('''
CREATE TABLE "files" (
    "id" TEXT NOT NULL,
    "upload_time" INTEGER,
    "is_deleted" BOOLEAN,
    PRIMARY KEY ("id")
)
''')

# 提交更改
conn.commit()

# 关闭连接
conn.close()