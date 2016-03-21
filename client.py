import select
import socket
import sys


class ChatClient:

    def __init__(self, server_ip, server_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_ip, server_port))
        self.socket.setblocking(False)

    def handle(self):
        fd_set = [sys.stdin, self.socket]
        while True:
            readable, _, _ = select.select(fd_set, [], [])
            for fd in readable:
                if fd == sys.stdin:
                    data = fd.readline().strip()
                    if data:
                        self.socket.sendall(data)
                elif fd == self.socket:
                    data = fd.recv(1024).strip()
                    if data:
                        sys.stdout.write(data + ' ')
                        sys.stdout.flush()

    def close(self):
        self.socket.close()


if len(sys.argv) > 2:
    client = ChatClient(sys.argv[1], int(sys.argv[2]))
    try:
        client.handle()
    except KeyboardInterrupt:
        client.close()
        print 'Goodbye!'
else:
    print 'Usage: python {} <server ip address> <sever port number>'.format(sys.argv[0])
