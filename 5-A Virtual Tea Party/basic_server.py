#@author: Neil
#2018-09-08

from asyncore import dispatcher
import socket, asyncore

PORT = 5005

class ChatServer(dispatcher):

    def __init__(self, port):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)  #指定要创建的套接字类型
        self.set_reuse_addr()  #地址重用
        self.bind(('', port))  #将服务器关联到特定地址
        self.listen(5)  #监听连接，最大连接数为5
        
    def handle_accept(self):
        conn, addr, = self.accept()  #允许客户端连接，返回套接字和地址
        print('Connection attempt from', addr[0])
        
if __name__ == '__main__':
    s = ChatServer(PORT)
    try:
        asyncore.loop()  #启动监听循环
    except KeyboardInterrupt:
        pass