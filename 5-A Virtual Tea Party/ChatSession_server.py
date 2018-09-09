#@author: Neil
#2018-09-08

from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore

PORT = 5005

class ChatSession(async_chat):
    """
    服务器运行后，每一个来自客户端的连接，都会被作为
    ChatSession类的参数，实例化为一个会话对象
    """
    
    def __init__(self, sock):
        async_chat.__init__(self, sock)
        self.set_terminator('\r\n'.encode())  #设置结束符为\r\n,(网络协议常用行结束符)
        self.data = []  #将已读取的数据存储在字符串列表
        self.push('欢迎进入聊天室！'.encode())
        
    def collect_incoming_data(self, data):  #读取和暂存数据
        self.data.append(data.decode())
        
    def found_terminator(self):  #遇到结束符时处理数据
        line = ''.join(self.data)  #内容整合为一行
        self.data = []  #清空数据列表
        print(line)  #打印

class ChatServer(dispatcher):

    def __init__(self, port):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)  #指定要创建的套接字类型
        self.set_reuse_addr()  #地址重用
        self.bind(('', port))  #将服务器关联到特定地址
        self.listen(5)  #监听连接，最大连接数为5
        self.sessions = []
        
    def handle_accept(self):
        conn, addr, = self.accept()  #允许客户端连接，返回套接字和地址
        self.sessions.append(ChatSession(conn))
        print('Connection attempt from', addr[0])
        
if __name__ == '__main__':
    s = ChatServer(PORT)
    try:
        asyncore.loop()  #启动监听循环
    except KeyboardInterrupt:
        pass