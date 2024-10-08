import sqlite3  
  
# 连接到数据库  
conn = sqlite3.connect('server/database.db')  
  
# 创建一个游标对象  
cur = conn.cursor()  
  
# 创建一个名为example_table的表  
cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')
cur.execute('''CREATE TABLE "chat_history" (
"id"  INTEGER NOT NULL,
"user_id"  INTEGER,
"target_id"  INTEGER,
"target_type"  TEXT,
"data"  BLOB,
"send_time" TIMESTAMP,
"sent"  INTEGER,
PRIMARY KEY ("id" ASC)
)''')
conn.commit() 
cur.execute('''DROP TABLE IF EXISTS "main"."friends"''')
cur.execute('''CREATE TABLE "friends" (
"from_user_id"  INTEGER NOT NULL,
"to_user_id"  INTEGER NOT NULL,
"accepted"  TEXT,            
PRIMARY KEY ("from_user_id" ASC, "to_user_id")
)''')
conn.commit() 
cur.execute('''DROP TABLE IF EXISTS "main"."rooms"''')
cur.execute('''CREATE TABLE "rooms" (
"id"  INTEGER NOT NULL,
"room_name"  TEXT,
"created_time" DATE,
"room_creator" TEXT,
PRIMARY KEY ("id")
)''')
conn.commit() 
cur.execute('''DROP TABLE IF EXISTS "main"."room_user"''')
cur.execute('''CREATE TABLE "room_user" (
"id"  INTEGER NOT NULL,
"room_id"  INTEGER,
"user_id"  INTEGER,
"is_admin"  INTEGER,
PRIMARY KEY ("id")
)''')
conn.commit() 
cur.execute('''DROP TABLE IF EXISTS "main"."users"''')
cur.execute('''CREATE TABLE "users" (
"id"  INTEGER NOT NULL,
"username"  TEXT,
"password"  TEXT,
"school_id"  TEXT,
"sex"  TEXT,
"role" TEXT,
"is_banned" INTERGER,
PRIMARY KEY ("id" ASC)
);''')
conn.commit() 
cur.execute('''DROP TABLE IF EXISTS "main"."announcements"''')
cur.execute('''CREATE TABLE "announcements" (
"id"  INTEGER NOT NULL,
"visible_to_students"  INTEGER DEFAULT 1,
"visible_to_teachers"  INTEGER DEFAULT 1,
"title" TEXT,
"content" TEXT,
"send_time" DATE,
"expiry_time" DATE,
PRIMARY KEY ("id" ASC)
);''')
cur.execute('''DROP TABLE IF EXISTS "main"."room_blacklists"''')
cur.execute('''CREATE TABLE "room_blacklists" (
"id"  INTEGER NOT NULL,
"room_id",
"user_id",
PRIMARY KEY ("id" ASC)
);''')
# cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')
# cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')
# cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')
# cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')
# cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')
# cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')
# cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')
# cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')
# cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')
# cur.execute('''DROP TABLE IF EXISTS "main"."chat_history"''')            
conn.commit()  
  
