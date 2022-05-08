import os
import paramiko
import socket
import sys
import threading

CWD =os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))   #   paramiko 官方提供的实列 ssh 密钥

class Server (paramiko.ServerInterface):    #   把这个监听器 SSH 化
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return  paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISSTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'tim') and (password == 'sekret'):
            return  paramiko.AUTH_SUCCESSFUL

if __name__ == '__main__':
    server = '172.16.16.4'
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))   #   打开一个socket 监听器
        sock.listen(100)
        print('[+] Listening for connection ...')
        client, addr = sock.accept()
    except Exception as e:
        print('[-] Listen failed: ' + str(e))
        sys.exit(1)
    else:
        print('[+] Got a connection!', client, addr)

    bhSession = paramiko.Transport(client)  #设置监听器的权限认证方式
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    bhSession.start_server(server=server)

    chan =bhSession.accept(20)
    if chan is None:
        print('*** No channel.')
        sys.exit(1)

    print('[+] Authenticated!') #   当客户端通过认证
    print(chan.recv(1024))  #   并向我们发送ClientConnected 命令后
    chan.send('Welcome to bh_ssh')
    try:
        while True:
            command= input("Enter command:")
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send('exit')
                print('exiting')
                bhSession.close()
                break

    except KeyboardInterrupt:
        bhSession.close()
