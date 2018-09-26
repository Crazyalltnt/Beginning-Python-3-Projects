#@author: Neil
#2018-09-24

from xmlrpc.client import ServerProxy, Fault  # 导入服务器代理类和故障类
from cmd import Cmd  # 导入命令类
from random import choice  # 导入随机选取的方法
from string import ascii_lowercase  # 导入小写字母列表对象
from server import Node, UNHANDLED  # 导入服务器中的节类和变量
from threading import Thread  # 导入线程类
from time import sleep
import sys

HEAD_START = 0.1 # 等待服务器启动时长0.1s
SECRET_LENGTH = 100  # 密钥长度

def random_string(length):
    """
    返回一个指定长度的由字母组成的随机字符串
    """
    chars = []
    letters = ascii_lowercase[:26]

    while length > 0:
        length -= 1
        chars.append(choice(letters))  # 随机获取小写字母叠加到变量
    return ''.join(chars)

class Client(Cmd):
    """
    一个基于文本的界面，用于访问Node类
    """

    prompt = '> '  # 重写超类中的命令提示符

    def __init__(self, url, dirname, urlfile):
        """
       设置URL、dirname和urlfile，并在一个独立的线程中启动Node服务器
        """
        Cmd.__init__(self)
        self.secret = random_string(SECRET_LENGTH)  # 创建密钥变量
        n = Node(url, dirname, self.secret)  # 创建节点对象
        t = Thread(target=n._start)  # 创建节点对象
        t.setDaemon(1)  # 将线程设置为守护线程
        t.start()  # 启动线程
        sleep(HEAD_START)  # 等待服务器启动
        self.server = ServerProxy(url)  # 创建服务器代理对象
        for line in open(urlfile):  # 读取URL文件
            line = line.strip()
            self.server.hello(line)  # 添加URL文件中的URL到已知节点集合

    def do_fetch(self, arg):
        "调用服务器的方法fetch"
        try:
            self.server.fetch(arg, self.secret)
        except Fault as f:  # 捕获故障异常
            if f.faultCode != UNHANDLED: raise  # 如果异常代码不是未找到文件不做处理
            print("Couldn't find the file", arg)

    def do_exit(self, arg):
        "退出程序"
        print()
        sys.exit()

    do_EOF = do_exit # End-Of-File 与 'exit'等价

def main():
    urlfile, directory, url = sys.argv[1:]
    client = Client(url, directory, urlfile)
    client.cmdloop()

if __name__ == '__main__': main()