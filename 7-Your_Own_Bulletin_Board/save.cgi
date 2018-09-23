#!/usr/bin/python

print('Content-type: text/html\n')

import cgitb; cgitb.enable()
import sqlite3

conn = sqlite3.connect('user=foo password=bar dbname=baz')  #连接数据库
curs = conn.cursor()  #获取游标对象

import cgi, sys
form = cgi.FieldStorage()

sender = form.getvalue('sender')
subject = form.getvalue('subject')
text = form.getvalue('text')
reply_to = form.getvalue('reply_to')

if not (sender and subject and text):
    print("""
    <html>

    <head>
    <title>Message Saved</title>
    </head>
    <body>
      <h1>消息保存失败</h1>
      <p>请提供标题、发信人和内容</p>
      <hr />
      <a href="edit.cgi">返回编辑</a>
     </body>
    </html>
    """)
    sys.exit()
else:
    if reply_to is not None:
        query = ("""
        INSERT INTO messages(reply_to, sender, subject, text)
        VALUES(%s, '%s', '%s', '%s')""" % (int(reply_to), sender, subject, text))
    else:
        query = ("""
        INSERT INTO messages(sender, subject, text)
        VALUES('%s', '%s', '%s')""" % (sender, subject, text))

    curs.execute(query)
    conn.commit()

    print("""
    <html>

    <head>
    <title>Message Saved</title>
    </head>
    <body>
      <h1>消息保存成功</h1>
      <hr />
      <a href='main.cgi'>返回首页</a>
     </body>
    </html>
    """)