#@author: Neil
#2018-09-24

from xmlrpc.client import ServerProxy, Fault  # 导入故障异常类Fault
from os.path import join, abspath, isfile  # 导入绝对路径的方法abspath
from xmlrpc.server import SimpleXMLRPCServer
from urllib.parse import urlparse
import sys

SimpleXMLRPCServer.allow_reuse_address = 1  # 保证节点服务器重启后能立即访问

MAX_HISTORY_LENGTH = 6

UNHANDLED     = 100  # 文件不存在的异常代码
ACCESS_DENIED = 200  # 文件访问受限的异常代码

class UnhandledQuery(Fault):
    """
    表示查询未得到处理的异常
    """
    def __init__(self, message="Couldn't handle the query"):  # 定义构造方法
        super().__init__(UNHANDLED, message)  # 重载超类构造方法

class AccessDenied(Fault):
    """
    用户试图访问未获得授权的资源时引发的异常
    """
    def __init__(self, message="Access denied"):
        super().__init__(ACCESS_DENIED, message)

def inside(dir, name):
    """
    检查指定的目录是否包含指定的文件
    """
    dir = abspath(dir)  # 获取共享目录的绝对路径
    name = abspath(name)  # 获取请求资源的绝对路径
    return name.startswith(join(dir, ''))  # 返回请求资源的路径是否以共享目录路径开始

def get_port(url):
    """
    Extracts the port number from a URL.
    """
    name = urlparse(url)[1]
    parts = name.split(':')
    return int(parts[-1])

class Node:
    """
    A node in a peer-to-peer network.
    """
    def __init__(self, url, dirname, secret):
        self.url = url
        self.dirname = dirname
        self.secret = secret
        self.known = set()

    def query(self, query, history=[]):
        """
        Performs a query for a file, possibly asking other known Nodes for
        help. Returns the file as a string.
        """
        try:
            return self._handle(query)
        except UnhandledQuery:
            history = history + [self.url]
            if len(history) >= MAX_HISTORY_LENGTH: raise
            return self._broadcast(query, history)

    def hello(self, other):
        """
        Used to introduce the Node to other Nodes.
        """
        self.known.add(other)
        return 0

    def fetch(self, query, secret):
        """
        Used to make the Node find a file and download it.
        """
        if secret != self.secret: raise AccessDenied
        result = self.query(query)
        f = open(join(self.dirname, query), 'w')
        f.write(result)
        f.close()
        return 0

    def _start(self):
        """
        Used internally to start the XML-RPC server.
        """
        s = SimpleXMLRPCServer(("", get_port(self.url)), logRequests=False)
        s.register_instance(self)
        s.serve_forever()

    def _handle(self, query):
        """
        Used internally to handle queries.
        """
        dir = self.dirname
        name = join(dir, query)
        if not isfile(name): raise UnhandledQuery  # 如果路径不是一个文件，抛出文件不存在的异常
        if not inside(dir, name): raise AccessDenied  # 如果请求的资源不是共享目录中的资源，抛出访问资源受限异常
        return open(name).read()  # 未发生异常时返回读取的文件数据

    def _broadcast(self, query, history):
        """
        Used internally to broadcast a query to all known Nodes.
        """
        for other in self.known.copy():
            if other in history: continue
            try:
                s = ServerProxy(other)
                return s.query(query, history)
            except Fault as f:   # 如果捕获访问故障异常获取异常代码
                if f.faultCode == UNHANDLED: pass  # 如果是文件不存在异常不做任何处理
                else: self.known.remove(other)  # 如果是其它故障异常从已知节点列表中移除节点
            except:  # 如果捕获其它异常（非故障异常）
                self.known.remove(other)  # 从已知节点列表中移除节点
        raise UnhandledQuery  # 如果已知节点都未能请求到资源，抛出文件不存在异常。

def main():
    url, directory, secret = sys.argv[1:]  #获取命令行参数
    n = Node(url, directory, secret)  #创建节点对象
    n._start()  # 启动节点服务器

if __name__ == '__main__': main()