#@author： Neil
#2018-09-06

from nntplib import NNTP, decode_header
from urllib.request import urlopen
import textwrap
import re

class NewsAgent:  #新闻代理
    """
    可将新闻源中的新闻分发到新闻目的地的对象
    """
    def __init__(self):  #初始化源列表和输出目标列表
        self.sources = []
        self.destinations = []
    
    def add_source(self, source):  #添加源
        self.sources.append(source)
        
    def addDestination(self, dest):  #添加输出目标
        self.destinations.append(dest)

    def distribute(self):
        """
        从所有新闻源获取所有新闻，并将其分发到新闻目的地
        """
        items = []
        for source in self.sources:  #遍历所有新闻源创建新闻列表
            items.extend(source.get_items())
        for dest in self.destinations:  #遍历所有输出目标并提供新闻列表
            dest.receive_items(items)

class NewsItem:  #新闻内容类
    """
    由标题和正文组成的简单新闻
    """
    def __init__(self, title, body):
        self.title = title
        self.body = body
        
class NNTPSource:  
    """
    从NNTP新闻组获取新闻的新闻源
    """
    def __init__(self, servername, group, howmany):
        self.servername = servername  #服务器地址
        self.group = group  #新闻组名称
        self.howmany = howmany  #数量
    
    def get_items(self):  #新闻生成器
        server = NNTP(self.servername)
        resp, count, first, last, name = server.group(self.group)  #新闻组信息列表
        start = last - self.howmany + 1
        resp, overviews = server.over((start, last))
        for id, over in overviews:
            title = decode_header(over['subject'])
            resp, info = server.body(id)
            body = '\n'.join(line.decode() for line in info.lines) + '\n\n'
            yield NewsItem(title, body)
        server.quit()
        
class SimpleWebSource:
    """
    使用正则表达式从网页提取新闻的新闻源
    """
    def __init__(self, url, title_pattern, body_pattern, encoding='utf-8'):
        self.url = url
        self.title_pattern = re.compile(title_pattern)
        self.body_pattern = re.compile(body_pattern)
        self.encoding = encoding
    
    def get_items(self):
        text = urlopen(self.url).read().decode(self.encoding)
        titles = self.title_pattern.findall(text)
        bodies = self.body_pattern.findall(text)
        for title, body in zip(titles, bodies):
            yield NewsItem(title, textwrap.fill(body) + '\n')

class PlainDestination:
    """
    以纯文本方式显示所有新闻的新闻目的地
    """
    def receive_items(self, items):
        for item in items:
            print(item.title)
            print('-' * len(item.title))
            print(item.body)
            
class HTMLDestination:
    """
    以HTML格式显示所有新闻的新闻目的地
    """
    def __init__(self, filename):
        self.filename = filename
        
    def receive_items(self, items):
        out = open(self.filename, 'w')
        print("""
        <html>
          <head>
            <title>Today's News</title>
          <head>
          <body>
          <h1>Today's News</h1>
        """, file=out)
        
        print('<ul>', file=out)
        id = 0
        for item in items:
            id += 1
            print('<li><a href="#{}">{}</a></li>'.format(id, item.title), file=out)
        print('</ul>', file=out)
        
        id = 0
        for item in items:
            id += 1
            print('<h2><a name="{}"></a></h2>'.format(id, item.title), file=out)
            print('<pre>{}</pre>'.format(item.body), file=out)
            
        print("""
          </body>
        <html>
        """, file=out)
        
def runDefaultSetup():
    """
    默认的新闻源和目的地设置，请根据偏好进行修改
    """
    agent = NewsAgent()
    
    #从路透社获取新闻的SimpleWebSource对象：
    #reuters_url = 'http://www.reuters.com/news/world'
    #reuters_title = r'<h2><a href="[^"]*"\s*>(.*?)</a>'
    #reuters_body = r'</h2><p>(.*?)</p>'
    
    #从36Kr获取新闻的SimpleWebSource对象：
    reuters_url = 'http://36kr.com/newsflashes'
    reuters_title = r'"pin":"0","title":"(.{10,60})","catch_title"'
    reuters_body = r'"description":"(.{100,400})","cover"'
    reuters = SimpleWebSource(reuters_url, reuters_title, reuters_body)
    
    agent.add_source(reuters)
     
    #从comp.lang.python获取新闻的NNTPSource对象：
    # clpa_server = 'news.foo.bar' Insert real server name
    clpa_server = 'web.aioe.org'
    clpa_group = 'comp.lang.python'
    clpa_howmany = 10
    clpa = NNTPSource(clpa_server, clpa_group, clpa_howmany)

    agent.add_source(clpa)
    
    #添加纯文本目的地和HTML目的地：
    agent.addDestination(PlainDestination())
    agent.addDestination(HTMLDestination('news.html'))
    
    #分发新闻：
    agent.distribute()

if __name__ == '__main__': runDefaultSetup()