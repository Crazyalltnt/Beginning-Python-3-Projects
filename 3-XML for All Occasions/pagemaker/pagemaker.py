#@authir: Neil
#2018-09-03

from xml.sax.handler import ContentHandler
from xml.sax import parse

class PageMaker(ContentHandler):    #事件处理程序自动调用

    passthrough = False    #指出当前是否在page标签内
    
    #元素开始事件处理
    def startElement(self, name, attrs):
        if name == 'page':
            self.passthrough = True
            self.out = open(attrs['name'] + '.html', 'w')
            self.out.write('<html><head>\n')
            self.out.write('<title>{}</title>\n'.format(attrs['title']))
            self.out.write('</head><body>\n')
        elif self.passthrough:
            self.out.write('<' + name)
            for key, val in attrs.items():
                self.out.write(' {}="{}"'.format(key, val))
            self.out.write('>')
            
    ##元素结束事件处理
    def endElement(self, name):
        if name == 'page':
            self.passthrough = False
            self.out.write('\n</body></html>\n')
            self.out.close()
        elif self.passthrough:
            self.out.write('</{}>'.format(name))

    #内容事件处理
    def characters(self, chars):
        if self.passthrough: self.out.write(chars)

parse('website.xml', PageMaker())   #读取文件并生成事件