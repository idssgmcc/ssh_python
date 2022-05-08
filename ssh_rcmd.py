import paramiko
import shlex
import subprocess

def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())    # paramiko支持密钥认证来代替密码验证
    client.connect(ip, port=port, username=user, password=passwd)

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())
        while True:
            command = ssh_session.recv(1024)    # 从ssh连接里不断读取命令
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close()
                    break
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)  # 在本地执行
                ssh_session.send(cmd_output or 'okay')  # 再返回服务器
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return

if __name__ == '__main__':
    import  getpass
    user = getpass.getuser()
    passwrod = getpass.getpass()

    ip = input('Enter server IP:')
    port = input('Enter port:')
    ssh_command(ip, port, user, passwrod, 'ClientConnected')

