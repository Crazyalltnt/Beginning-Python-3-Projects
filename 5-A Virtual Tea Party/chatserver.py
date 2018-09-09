#@author: Neil
#2018-09-09

from asyncore import dispatcher
from asynchat import async_chat
import asyncore, socket

PORT = 5005  #端口号 
NAME = 'TestChat'  #自定义聊天中心名称 

class EndSession(Exception): pass

class CommandHandler:
    """
    类似于标准库中cmd.Cmd的简单命令处理程序
    """
    
    def unknown(self, session, cmd):
        '响应未知命令'
        session.push('Unknown command: {}\r\n'.format(cmd).encode())

    def handle(self, session, line):
        '处理从指定会话收到的行'
        if not line.strip(): return
        # 提取命令
        parts = line.split(' ', 1)
        cmd = parts[0]
        try: line = parts[1].strip()
        except IndexError: line = ''
        # 尝试查找处理程序
        meth = getattr(self, 'do_' + cmd, None)
        try:
            # 假设可调用:
            meth(session, line)
        except TypeError:
            # 如果不可调用，响应未知命令
            self.unknown(session, cmd)

class Room(CommandHandler):
    """
    可能包含一个或多个用户（会话）的通用环境，它负责基本的命令处理和广播
    """

    def __init__(self, server):
        self.server = server
        self.sessions = []

    def add(self, session):
        '有会话（用户）进入聊天室'
        self.sessions.append(session)

    def remove(self, session):
        '有会话（用户）离开聊天室'
        self.sessions.remove(session)

    def broadcast(self, line):
        '将一行内容发送给聊天室内所有会话'
        for session in self.sessions:
            session.push(line.encode())

    def do_logout(self, session, line):
        '响应命令logout'
        raise EndSession

class LoginRoom(Room):
    """
    为刚连接的用户准备的聊天室
    """

    def add(self, session):
        Room.add(self, session)
        # 用户进入时向他/她发出问候
        self.broadcast('Welcome to {}\r\n'.format(self.server.name))

    def unknown(self, session, cmd):
        # 除login和logout外所有未知命令将导致系统显示提醒消息
        session.push('Please log in\nUse "login <nick>"\r\n'.encode())

    def do_login(self, session, line):
        name = line.strip()
        # 确保用户输入了用户名
        if not name:
            session.push('Please enter a name\r\n'.encode())
        # 确保用户名未被占用
        elif name in self.server.users:
            session.push('The name "{}" is taken.\r\n'.format(name).encode())
            session.push('Please try again.\r\n'.encode())
        else:
            # 用户名没问题，因此将其存储到会话中并将用户移到主聊天室
            session.name = name
            session.enter(self.server.main_room)

class ChatRoom(Room):
    """
    为多个用户相互聊天准备的聊天室
    """

    def add(self, session):
        # 通知所有人有新用户进入
        self.broadcast(session.name + ' has entered the room.\r\n')
        self.server.users[session.name] = session
        super().add(session)

    def remove(self, session):
        Room.remove(self, session)
        # 通知所有人有用户离开
        self.broadcast(session.name + ' has left the room.\r\n')

    def do_say(self, session, line):
        self.broadcast(session.name + ': ' + line + '\r\n')

    def do_look(self, session, line):
        '处理命令look,用于查看聊天室里都有谁'
        session.push('The following are in this room:\r\n'.encode())
        for other in self.sessions:
            session.push((other.name + '\r\n').encode())

    def do_who(self, session, line):
        '处理命令who,用于查看谁已登录'
        session.push('The following are logged in:\r\n'.encode())
        for name in self.server.users:
            session.push((name + '\r\n').encode())

class LogoutRoom(Room):
    """
    为单个用户准备的聊天室，用于将用户名从服务器删除
    """

    def add(self, session):
        # 删除进入LogoutRoom的用户
        try: del self.server.users[session.name]
        except KeyError: pass
            
class ChatSession(async_chat):
    """
    单个会话，负责与单个用户通信
    """
    def __init__(self, server, sock):
        super().__init__(sock)  #初始化父类
        self.server = server  #记录session的服务器
        self.set_terminator(("\r\n").encode())  #设置触发found_terminator条件
        self.data = []
        self.name = None
        #所有会话最初都位于LoginRoom
        self.enter(LoginRoom(server))
        
    def enter(self, room):
        # 自己从当前聊天室离开并进入下一聊天室
        try: cur = self.room
        except AttributeError: pass
        else: cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):  #读取和暂存数据
        self.data.append(data.decode())

    def found_terminator(self):  #触发该函数时，调用服务器函数发送数据给客户端
        line = ''.join(self.data)
        self.data = []
        try: self.room.handle(self, line)
        except EndSession: self.handle_close()

    def handle_close(self):  #定义客户端断开连接的处理方法
        async_chat.handle_close(self)  #重载超类中的方法
        self.enter(LogoutRoom(self.server))  #从会话列表中移除当前会话

class ChatServer(dispatcher):
    """
    接受连接并创建会话，向其广播
    """
    def __init__(self, port, name):
        super().__init__()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()  #保证服务器未正常关闭时，再次开启服务器能够重用端口号。
        self.bind(('', port))  #将服务器关联到特定地址
        self.name = name
        self.listen(5)
        self.users = {}
        self.main_room = ChatRoom(self)
            
    def handle_accept(self):
        #当客户端连接该端口的时候运行此函数
        conn, addr = self.accept()  #同意连接
        ChatSession(self, conn)

if __name__=='__main__':
    s = ChatServer(PORT, NAME)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print('服务器已关闭！')