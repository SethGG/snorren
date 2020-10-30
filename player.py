from flask_login import UserMixin


class Player(UserMixin):
    def __init__(self, name, sid, game):
        self.name = name
        self.sid = sid
        self.game = game
        self.role = None
        self.dead = False
        self.lover = False
        self.mayor = False
        self._info = {}

    def get_id(self):
        return self.sid

    @property
    def is_active(self):
        return bool(self.sid)
