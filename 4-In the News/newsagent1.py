#@author： Neil
#2018-09-05

from nntplib import NNTP

servername = 'web.aioe.org' #NNTP服务器
group = 'comp.lang.python'  #新闻组
server = NNTP(servername)
howmany = 10    #指定获取文章数量
#返回通用的服务器响应、新闻组包含的消息数、第一条和最后一条消息的编号以及新闻组名称
resp, count, first, last, name = server.group(group)

start = last - howmany +1   #编号区间起点

resp, overviews = server.over((start, last))    #返回消息
for id, over in overviews:
    subject = over['subject']
    resp, info = server.body(id)
    print(subject)
    print('-' * len(subject))
    for line in info.lines:
        print(line.decode('latin1'))
    print()
    
server.quit()