import os
import sha
import SocketServer
import sys
import time
import util


class User:

    def __init__(self, username, password_sha, login_socket=None,
            login_ip=None, last_active=None, blocked_ips=None):
        self.username = username
        self.password_sha = password_sha
        self.login_socket = login_socket
        self.login_ip = login_ip
        self.last_active = last_active or float('-inf')
        self.blocked_ips = blocked_ips or {}

    def is_active(self):
        return self.login_socket is not None

    def login(self, login_socket, login_ip, last_active):
        self.login_socket = login_socket
        self.login_ip = login_ip
        self.last_active = int(time.time())

    def logout(self):
        self.login_socket = None

    def send_message(self, message, from_user):
        self.login_socket.sendall('[{}] {}: {}\n> '.format(
            time.strftime('%m/%d/%y% at %H:%M:%S'),
            from_user.username,
            message,
        ))


class ChatServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self, server_address, request_handler_class):
        SocketServer.TCPServer.__init__(self,server_address, request_handler_class)
        self.load_users('user_pass.txt')
        self.daemon_threads = True  # allow threads to run autonomously upon shutdown
        os.environ['BLOCK_TIME'] = '60'

    def load_users(self, path):
        self.users = {}
        username_sha_pairs = [line.strip().split(',') for line in open(path, 'r')]
        for username, password_sha in username_sha_pairs:
            self.add_user(username, password_sha)

    def add_user(self, username, password_sha):
        self.users[username] = User(username, password_sha)


class ChatRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        try:
            self.log('Connection established')
            if self.authenticate():
                self.user.login(self.request, self.ip)
                self.request.sendall('Welcome, {}!\n'.format(self.user.username))
                client_input = None
                while client_input != 'logout':
                    client_input = self.prompt('> ')
                    self.user.last_active = int(time.time())
                    self.process_command(client_input)
                self.user.logout()
            self.log('Connection terminated')
        except Exception as exception:
            self.log('Connection lost')

    def authenticate(self):
        self.user = None
        while not self.user:
            username = self.prompt('username: ')
            user = self.server.users.get(username)
            if not user:
                register = self.prompt(
                    'Invalid username. '
                    'Do you wish to register a new user? [y/n] '
                )
                if register == 'y':
                    password = self.prompt('password: ')
                    while password != self.prompt('verify password: '):
                        self.request.sendall('Passwords don\'t match. Try again\n')
                        password = self.prompt('password: ')
                    self.register_user(username, password)
            elif self.ip in user.blocked_ips:
                current_time = int(time.time())
                time_elapsed = current_time - user.blocked_ips[self.ip]
                time_left = self.block_time - time_elapsed
                if time_elapsed > self.block_time:
                    user.blocked_ips.pop(self.ip)
                    self.user = user
                else:
                    self.request.sendall(
                        'Logins for {} from {} were blocked {} seconds ago. '
                        'Please try again in {} seconds.\n'.format(
                            user.username, self.ip, time_elapsed, time_left
                         )
                    )
                    return False
            elif user.is_active():
                self.request.sendall('Username already active\n')
            else:
                self.user = user
        login_attempts = 0
        while login_attempts < 3:
            password = self.prompt('password: ')
            if self.user.password_sha == util.sha1_hex(password):
                return True
            login_attempts += 1
        self.request.sendall(
            'Three failed login attempts. '
            'Please try again in {} seconds'.format(self.block_time)
        )
        self.user.blocked_ips[self.ip] = int(time.time())
        return False

    def register_user(self, username, password):
        password_sha = util.sha1_hex(password)
        self.server.add_user(username, password_sha)
        with open('user_pass.txt', 'a') as pwd_file:
            pwd_file.write('{},{}\n'.format(username, password_sha))

    def process_command(self, command_string):
        command, args = util.parse_command(command_string)
        if command == 'who':
            self.who()
        elif command == 'last':
            try:
                number = int(args[0])
                self.last(number)
            except Exception:
                self.request.sendall('last: invalid argument\n')
        elif command == 'broadcast':
            message = ' '.join(args)
            self.broadcast(message)
        elif command == 'send':
            try:
                usernames = set(args[0] if isinstance(args[0], list) else [args[0]])
                users = filter(None, [self.server.users.get(username) for username in usernames])
                message = ' '.join(args[1:])
                self.send(message, users)
            except Exception as error:
                self.request.sendall('send: invalid argument(s)\n')
        else:
            self.request.sendall('Invalid command\n')

    def who(self):
        message = ''
        for user in self.server.users.values():
            if user.is_active():
                message += user.username
                message += '\n'
        self.request.sendall(message)

    def last(self, number):
        message = ''
        current_time = int(time.time())
        for user in self.server.users.values():
            minutes = float(current_time - user.last_active) / 60
            if user.is_active() or minutes < number:
                message += user.username
                message += '\n'
        self.request.sendall(message)

    def broadcast(self, message):
        self.send(message, self.server.users.values())

    def send(self, message, users):
        for user in users:
            if user is not self.user and user.is_active():
                user.send_message(message, self.user)

    def prompt(self, string):
        self.request.sendall(string)
        return self.request.recv(1024).strip()

    @property
    def ip(self):
        return self.client_address[0]

    @property
    def block_time(self):
        return int(os.environ['BLOCK_TIME'])

    def log(self, message):
        print '[{}] {}: {}'.format(
            time.strftime('%m/%d/%y at %H:%M:%S'),
            self.ip,
            message,
        )


if len(sys.argv) > 1:
    port_number = int(sys.argv[1])
    server_address = ('localhost', port_number)
    server = ChatServer(server_address, ChatRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Goodbye!'
        server.shutdown()
else:
    print 'Usage: python {} <port number>'.format(sys.argv[0])
