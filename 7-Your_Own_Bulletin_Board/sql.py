import sqlite3

conn = sqlite3.connect('user=foo password=bar dbname=baz')
curs = conn.cursor()

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

curs.execute(sql)
curs.execute(table)
conn.commit()  # 提交数据操作