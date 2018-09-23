#@author: Neil
#2018-09-23

print('Content-type: text/html\n')

import cgitb; cgitb.enable()
import sqlite3

conn = sqlite3.connect('user=foo password=bar dbname=baz')  #连接数据库
curs = conn.cursor()  #获取游标对象

import cgi, sys
form = cgi.FieldStorage()
reply_to = form.getvalue('reply_to')

print("""
<html>
  <head>
    <title>Compose Message</title>
  </head>
  <body>
    <h1>撰写消息</h1>
    
    <form action='save.cgi' method='POST'>
    """)

subject = ''
if reply_to is not None:
    print('<input type="hidden" name="reply_to" value="{}"/>'.format(reply_to))
    curs.execute('SELECT subject FROM messages WHERE id = {}'.format(reply_to))
    subject = curs.fetchone()[0]
    if not subject.startswith('Re: '):
        subject = 'Re: ' + subject

print("""
     <b>标题：</b><br />
     <input type='text' size='40' name='subject' value='{}' /><br />
     <b>发送人：</b><br />
     <input type='text' size='40' name='sender' /><br />
     <b>消息：</b><br />
     <textarea name='text' cols='40' rows='20'></textarea><br />
     <input type='submit' value='保存'/>
     </form>
     <hr />
     <a href='main.cgi'>返回首页</a>
  </body>
</html>
""".format(subject))