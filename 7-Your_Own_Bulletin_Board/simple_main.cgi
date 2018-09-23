#@author: Neil
#2018-09-14

print('Content-type: text/html\n')

import cgitb; cgitb.enable()
import sqlite3

conn = sqlite3.connect('user=foo password=bar dbname=baz')  #连接数据库
curs = conn.cursor()  #获取游标对象


print("""
<html>
  <head>
    <title>The FooBar Bulletin Board</title>
  </head>
  <body>
    <h1>The FooBar Bulletin Board</h1>
    """)

curs.execute('SELECT * FROM messages')  #执行sql语句
names = [d[0] for d in curs.description]
rows = [dict(zip(names, row)) for row in curs.fetchall()]

toplevel = []  #保存父级消息的列表
children = {}  #保存子级消息的列表

for row in rows:  #遍历返回的消息列表
    parent_id = row['reply_to']  #获取消息源组中的列
    if parent_id is None:  #如果不是回复的消息
        toplevel.append(row)  #添加至父级列表
    else:
        children.setdefault(parent_id, []).append(row)   #否则以被回复消息的序号为键添加回复消息到值的列表
def format(row):
    print(row['subject'])
    try: kids = children[row['id']]
    except KeyError: pass
    else:
        print('<blockquote>')
        for kid in kids:
            format(kid)
        print('</blockquote>')
            
print('<p>')
  
for row in toplevel:
    format(row)
        
print("""
    </p>
  </body>
</html>
""")