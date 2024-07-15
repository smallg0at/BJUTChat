import sqlite3  
  
# 连接到数据库  
conn = sqlite3.connect('server/database.db')  
  
# 创建一个游标对象  
cur = conn.cursor()  
  
# 创建一个名为example_table的表  
cur.execute('''INSERT INTO announcements (title, content, send_time) VALUES (?,?,?)''', ["公告1", "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce ultricies massa elit, ac sollicitudin turpis ornare viverra. Praesent eget rutrum massa. Praesent consectetur et enim et malesuada. Curabitur a massa et ligula gravida eleifend at eget sem. Donec mollis, lorem sit amet sollicitudin ultrices, nisi nibh aliquam nisi, quis ullamcorper sem nibh eget ante. Mauris aliquet a nulla luctus sagittis. Etiam sodales tortor sed est sagittis imperdiet. Cras urna leo, suscipit sed nisi vel, feugiat pellentesque odio. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus vitae ex fringilla, mollis lorem gravida, tincidunt sem. Integer luctus, neque nec hendrerit euismod, enim ex sagittis nulla, vel rutrum quam justo id lectus. Suspendisse in metus vitae elit viverra aliquam.", 1721029072])
conn.commit()  
  
