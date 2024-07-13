import sqlite3  
  
# 连接到数据库  
conn = sqlite3.connect('server/database.db')  
  
# 创建一个游标对象  
cur = conn.cursor()  
  
# 创建一个名为example_table的表  
cur.execute('''UPDATE "main"."users"
            SET is_banned=1
            WHERE id=1''')
conn.commit()  
  
