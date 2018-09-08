#@author: Neil
#2018-09-08

from asyncore import dispatcher
from asynchat import async_chat
import asyncore, socket

PORT = 5005#端口号 
NAME = 'TestChat'#自定义聊天中心名称 

class ChatSession(async_chat):
    '''
    Session类， 记录客户端发送来的内容
    '''
    def __init__(self, server, sock):
        async_chat.__init__(self, sock)#初始化父类
        self.server = server#记录session的服务器
        self.set_terminator(("\r\n").encode())#设置触发found_terminator条件
        self.data = []
        welcome = 'Welcome to %s\r\n' % self.server.name
        self.push(welcome.encode())#压入欢迎字符串

    def collect_incoming_data(self, data):
        self.data.append(data.decode())

    def found_terminator(self):
        #触发该函数时，调用服务器函数发送数据给客户端
        line = ''.join(self.data)
        self.data = []
        self.server.broadcast(line)

    def handle_close(self):
        async_chat.handle_close(self)
        self.server.disconnect(self)

class ChatServer(dispatcher):
    def __init__(self, port, name):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.name = name
        self.listen(5)
        self.sessions = []

    def disconnect(self, session):
        #移除指定的session
        self.sessions.remove(session)

    def broadcast(self, line):
        #向每个客户端发送消息
        for session in self.sessions:
            session.push((line + '\r\n').encode())
            
    def handle_accept(self):
        #当客户端连接该端口的时候运行此函数
        conn, addr = self.accept()#同意连接
        print('Connnetion attempt from', addr[0])#打印客户端地址
        self.sessions.append(ChatSession(self, conn))#创建客户与服务器之间session

if __name__=='__main__':
    s = ChatServer(PORT, NAME)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print()