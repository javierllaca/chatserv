from Queue import Queue
import util


class User:

    def __init__(self, username, password_sha):
        self.username = username
        self.password_sha = password_sha
        self.socket = None
        self.ip = None
        self.last_active = float('-inf')
        self.blocked_ips = {}
        self.message_queue = Queue()

    def login(self, socket, ip):
        self.socket = socket
        self.ip = ip
        self.last_active = util.current_time()

    def logout(self):
        self.socket = None

    def enqueue_message(self, message):
        self.message_queue.put(message)

    def dump_message_queue(self):
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        return messages

    @property
    def is_connected(self):
        return self.socket is not None
