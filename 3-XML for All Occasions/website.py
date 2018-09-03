#@authir: Neil
#2018-09-03

from xml.sax.handler import ContentHandler
from xml.sax import parse
import os

class Dispatcher:
    """
    查找合适的处理程序,创建参数元素并使用
    这些参数调用处理程序
    """
    def dispatch(self, prefix, name, attrs=None):
        mname = prefix + name.capitalize()
        dname = 'default' + prefix.capitalize()
        method = getattr(self, mname, None) #获取处理程序
        if callable(method):
            args = ()
        else:
            method = getattr(self, dname, None) #不可调用时使用默认处理程序
            args = name,
        if prefix == 'start':
            args += attrs,  #合并参数元组为新的参数元组
        if callable(method):
            method(*args)   #传入参数调用方法，*拆分参数
        
    def startElement(self, name, attrs):    #开始元素方法
        self.dispatch('start', name, attrs)
    
    def endElement(self, name): #结束元素方法
        self.dispatch('end', name)
        
class WebsiteConstructor(Dispatcher, ContentHandler):
    
    passthrough = False #指出当前是否在标签内
    
    def __init__(self, directory):
        self.directory = [directory]    #创建目录列表
        self.ensureDirectory()  #创建根目录
    
    #确保目录创建好
    def ensureDirectory(self):
        path = os.path.join(*self.directory) #组合路径
        os.makedirs(path, exist_ok=True)    #创建多级目录树
    
    #读取到标记内容方法
    def characters(self, chars):
        if self.passthrough:    #在标签内打印内容
            self.out.write(chars)
            
    def defaultStart(self, name, attrs):
        if self.passthrough:
            self.out.write('<' + name)
            for key, val in attrs.items():
                self.out.write(' {}="{}"'.format(key, val))
            self.out.write('>')
            
    def defaultEnd(self, name):
        if self.passthrough:
            self.out.write('</{}>'.format(name))
    
    #读取到目录开始标记的方法
    def startDirectory(self, attrs):
        self.directory.append(attrs['name'])    #将目录加入目录列表
        self.ensureDirectory()
    
    #读取到目录开始标记的方法
    def endDirectory(self):
        self.directory.pop()    #弹出目录
    
    def startPage(self, attrs):
        filename = os.path.join(*self.directory + [attrs['name'] + '.html'])  #创建页面路径
        self.out = open(filename, 'w')
        self.writeHeader(attrs['title'])
        self.passthrough = True
    
    def endPage(self):
        self.passthrough = False
        self.writeFooter()
        self.out.close()
        
    def writeHeader(self, title):
        self.out.write('<html>\n  <head\n  <title>>')
        self.out.write(title)
        self.out.write('</title\n  </head>\n  <body>\n')
        
    def writeFooter(self):
        self.out.write('\n  </body>\n</html>\n')
        
parse('website.xml', WebsiteConstructor('public_html')) #调用解析函数