import sqlite3

conn = sqlite3.connect('user=foo password=bar dbname=baz')
curs = conn.cursor()

subject = input('标题：')
sender = input('发送人：')
reply_to = input('回复给：')
text = input('内容：')

sql = "drop table if exists messages"

table = """
create table if not exists messages (
    id          integer primary key autoincrement,
    subject     text not null,
    sender      text not null,
    reply_to    int,
    text        text not null
);
"""

if reply_to:  # 如果是回复已有消息
    query = """
    INSERT INTO messages(reply_to, sender, subject, text)
    VALUES({}, '{}', '{}', '{}')""".format(reply_to, sender, subject, text)
else:  # 否则是发布新的消息
    query = """
    INSERT INTO messages(sender, subject, text)
    VALUES('{}', '{}', '{}')""".format(sender, subject, text)

curs.execute(sql)
curs.execute(table)
curs.execute(query)
conn.commit()  # 提交数据操作
#query  = 'select * from messages'
#curs.execute(query)
#print(curs.fetchall())
