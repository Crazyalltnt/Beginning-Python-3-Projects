#@author: Neil
#2018-09-23

print('Content-type: text/html\n')

import cgitb; cgitb.enable()
import sqlite3

conn = sqlite3.connect('user=foo password=bar dbname=baz')  #连接数据库
curs = conn.cursor()  #获取游标对象

import cgi, sys
form = cgi.FieldStorage()
id = form.getvalue('id')

print("""
<html>
  <head>
    <title>View Message</title>
  </head>
  <body>
    <h1>查看消息</h1>
    """)

try: id = int(id)
except:
    print('Invalid message ID')
    sys.exit()

curs.execute('SELECT * FROM messages WHERE id = {}'.format(id))
names = [d[0] for d in curs.description]
rows = [dict(zip(names, row)) for row in curs.fetchall()]

if not rows:
    print('Unknown message ID')
    sys.exit()
    
row = rows[0]

print("""
    <p><b>标题：</b>{subject}<br />
    <b>发送人：</b>{sender}<br />
    <pre>{text}</pre>
    </p>
    <hr />
    <a href='main.cgi'>返回首页</a>
    | <a href="edit.cgi?reply_to={id}">回复</a>
  </body>
</html>
""".format(**row))