#@author: Neil
#2018-09-24

from xmlrpc.client import ServerProxy
from os.path import join, isfile
from xmlrpc.server import SimpleXMLRPCServer
from urllib.parse import urlparse
import sys

MAX_HISTORY_LENGTH = 6  # 访问链最大长度

OK = 1  # 查询状态正常
FAIL = 2  # 查询状态无效
EMPTY = ''

def get_port(url):
    '从URL中提取端口'
    name = urlparse(url)[1]  # 解析并获取URL中[域名:端口]
    parts = name.split(':')  # 获取以分号结束最后一组
    return int(parts[-1])


class Node:
    """
    P2P网络中的节点
    """
    def __init__(self, url, dirname, secret):
        self.url = url
        self.dirname = dirname
        self.secret = secret
        self.known = set()

    def query(self, query, history=[]):
        """
        查询文件（可能向已知节点寻求帮助），并以字符串的方式返回它
        """
        code, data = self._handle(query)  # 获取处理请求的结果
        if code == OK:  # 如果正常状态
            return code, data  # 返回状态和数据
        else:
            history = history + [self.url]  # 历史记录添加已请求过的节点
            if len(history) >= MAX_HISTORY_LENGTH:  # 如果历史请求超过六次
                return FAIL, EMPTY  # 反返回无效状态和空数据
            return self._broadcast(query, history)  # 返回广播结果

    def hello(self, other):
        """
        用于向其他节点介绍当前节点
        """
        self.known.add(other)
        return OK

    def fetch(self, query, secret):
        """
        用于让节点查找并下载文件
        """
        if secret != self.secret: return FAIL  # 匹配密钥
        code, data = self.query(query)  # 处理请求获取文件状态与数据
        if code == OK:
            f = open(join(self.dirname, query), 'w')  # 写入模式打开
            f.write(data)  # 将获取到的数据写入文件
            f.close()
            return OK
        else:
            return FAIL

    def _start(self):
        """
        供内部用来启动XML-RPC服务器
        """
        s = SimpleXMLRPCServer(("", get_port(self.url)), logRequests=False)
        s.register_instance(self)  # 注册类的实例到服务器对象
        s.serve_forever()

    def _handle(self, query):
        """
        供内部用来处理查询
        """
        dir = self.dirname
        name = join(dir, query)  # 获取请求路径
        if not isfile(name): return FAIL, EMPTY  # 判断路径是否文件
        return OK, open(name).read()

    def _broadcast(self, query, history):
        """
        供内部用来向所有已知节点广播查询
        """
        for other in self.known.copy():  # 遍历已知节点的列表
            if other in history: continue  # 如果已知节点存在于历史记录继续下一节点
            try:
                s = ServerProxy(other)  # 访问非历史记录中的已知节点
                code, data = s.query(query, history)  # 向已知节点发出请求
                if code == OK:  # 如果状态为正常
                    return code, data  # 返回有效状态和数据
            except:
                self.known.remove(other)  # 如果发生异常，从已知节点列表移除节点
        return FAIL, EMPTY  # 返回无效状态和空数据

def main():
    url, directory, secret = sys.argv[1:]
    n = Node(url, directory, secret)
    n._start()

if __name__ == '__main__': main()