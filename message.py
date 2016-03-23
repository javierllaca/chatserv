import util


class Message:

    def __init__(self, message_string, from_user, to_user):
        self.message_string = message_string
        self.from_user = from_user
        self.to_user = to_user
        self.timestamp = util.current_time_string()

    def __str__(self):
        return '[{}] {}: {}'.format(
            self.timestamp,
            self.from_user.username,
            self.message_string
        )
