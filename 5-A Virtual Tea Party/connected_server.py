#@author: Neil
#2018-09-08

from asyncore import dispatcher
import socket, asyncore

class ChatServer(dispatcher):
    def handle_accept(self):
        conn, addr = self.accept()  #允许客户端连接，返回套接字和地址
        print('Connection attempt from', addr[0])
        
s = ChatServer()
s.create_socket(socket.AF_INET, socket.SOCK_STREAM)  #指定要创建的套接字类型
s.bind(('', 5005))  #将服务器关联到特定地址
s.listen(5)  #监听连接，最大连接数为5
asyncore.loop()  #启动监听循环