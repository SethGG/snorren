from flask import request
from flask_login import UserMixin

# ------------------------------------------------------------------------------------------------ #
# Player and GameMaster class
# ------------------------------------------------------------------------------------------------ #


class Player(UserMixin):
    def __init__(self, name):
        self.name = name
        self.sid = request.sid
        self.role = None

    def get_id(self):
        return self.sid

    @property
    def is_active(self):
        return bool(self.sid)

    @is_active.setter
    def is_active(self, bool):
        if bool and not self.sid:
            self.sid = request.sid
        elif not bool:
            self.sid = None


class GameMaster(Player):
    def __init__(self):
        Player.__init__(self, None)
        self.role = 'game master'
