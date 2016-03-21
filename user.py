import time

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

    def login(self, login_socket, login_ip):
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
