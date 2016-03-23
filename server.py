from chat_objects import Message, User
import os
import socket
import SocketServer
import sys
import user
import util

BUFFER_SIZE = 1024


class ChatServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self, server_address, request_handler_class, user_file_path):
        SocketServer.TCPServer.__init__(
            self,
            server_address,
            request_handler_class
        )
        self.load_users(user_file_path)
        self.daemon_threads = True

    def load_users(self, file_path):
        self.users = {}
        for line in open(file_path, 'r'):
            username, password_sha = line.strip().split(',')
            self.add_user(username, password_sha)

    def add_user(self, username, password_sha):
        self.users[username] = User(username, password_sha)


class ChatRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        self.request.settimeout(self.time_out)
        self.user = None
        try:
            self.log('Connection established')
            if self.authenticate():
                self.user.login(self.request, self.ip)
                self.log('{} logged in'.format(self.user.username))
                while self.user.is_connected:
                    self.send_messages()
                    client_input = self.recv()
                    self.user.last_active = util.current_time()
                    self.process_command(client_input)
            self.log('Connection terminated')
        except socket.timeout:
            self.send_line('timeout')
            self.log('Connection timeout')
        except Exception:
            self.log('Connection lost')
        finally:
            if self.user and self.user.is_connected:
                self.user.logout()
                self.log('{} logged out'.format(self.user.username))

    def authenticate(self):
        while not self.user:
            username = self.recv()
            user = self.server.users.get(username)
            if not user:
                self.send_line('register')
                register = self.recv()
                if register == 'y':
                    self.send_line('password')
                    password = self.recv()
                    while password != self.recv():
                        self.send_line('password')
                        password = self.recv()
                    self.send_line('registered')
                    self.register_user(username, password)
                else:
                    self.send_line('username')
            elif self.ip in user.blocked_ips:
                time_blocked = user.blocked_ips[self.ip]
                time_elapsed = util.current_time() - time_blocked
                time_left = self.block_time - time_elapsed
                if time_elapsed > self.block_time:
                    user.blocked_ips.pop(self.ip)
                    self.user = user
                else:
                    self.send_line('blocked,{}'.format(time_left))
                    return False
            elif user.is_connected:
                self.send_line('connected')
            else:
                self.user = user
        login_attempts = 0
        while login_attempts < 3:
            self.send_line('password')
            password = self.recv()
            if self.user.password_sha == util.sha1_hex(password):
                self.send_line('welcome')
                return True
            login_attempts += 1
        self.send_line(str(self.block_time))
        self.user.blocked_ips[self.ip] = util.current_time()
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
                self.send_line('error:args:{}'.format(command))
        elif command == 'broadcast':
            message_string = ' '.join(args)
            self.broadcast(message_string)
        elif command == 'send':
            try:
                usernames = set(
                    args[0] if isinstance(args[0], list) else [args[0]]
                )
                message_string = ' '.join(args[1:])
                self.send(message_string, usernames)
            except Exception:
                self.send_line('error:args:{}'.format(command))
        elif command == 'logout':
            self.send_line('goodbye')
            self.user.logout()
            self.log('{} logged out'.format(self.user.username))
        elif command == 'fetch':
            self.send_line('fetching')
        else:
            self.send_line('error:command:{}'.format(command))

    def send_messages(self):
        messages = self.user.dump_message_queue()
        for message in messages:
            self.send_line(str(message))
        self.send_line('DONE')
        if messages:
            self.log('{} received {} message(s)'.format(
                self.user.username,
                len(messages)
            ))

    def who(self):
        usernames = []
        for user in self.server.users.values():
            if user.is_connected:
                usernames.append(user.username)
        self.send_line(' '.join(usernames))

    def last(self, number):
        usernames = []
        ref_time = util.current_time()
        for user in self.server.users.values():
            minutes = float(ref_time - user.last_active) / 60
            if user.is_connected or minutes < number:
                usernames.append(user.username)
        self.send_line(' '.join(usernames))

    def broadcast(self, message):
        self.send(message, self.server.users.keys())

    def send(self, message_string, usernames):
        invalid_usernames, users_messaged = [], 0
        for username in usernames:
            user = self.server.users.get(username)
            if not user:
                invalid_usernames.append(username)
            elif user is not self.user:
                message = Message(message_string, self.user)
                user.enqueue_message(message)
                users_messaged += 1
        self.send_line('sent:{}'.format(''.join(invalid_usernames)))
        self.log('{} sent a message to {} user(s)'.format(
            self.user.username,
            users_messaged
        ))

    def recv(self):
        data = self.request.recv(BUFFER_SIZE).strip()
        if not data:
            raise socket.error
        return data

    def send_line(self, string):
        self.request.sendall('{}\n'.format(string))

    def log(self, message):
        print '[{}] {}: {}'.format(
            util.current_time_string(),
            self.ip,
            message,
        )

    @property
    def ip(self):
        return self.client_address[0]

    @property
    def block_time(self):
        return int(os.environ.get('BLOCK_TIME') or 60)

    @property
    def time_out(self):
        return int(os.environ.get('TIME_OUT') or 30 * 60)


if len(sys.argv) > 1:
    ip_address, port_number = 'localhost', int(sys.argv[1])
    server_address = (ip_address, port_number)
    server = ChatServer(server_address, ChatRequestHandler, 'user_pass.txt')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Goodbye!'
    finally:
        server.shutdown()
else:
    print 'Usage: python {} <port>'.format(sys.argv[0])
