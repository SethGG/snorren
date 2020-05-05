from flask import request
from flask_login import UserMixin
import globals as g

# ------------------------------------------------------------------------------------------------ #
# Player and GameMaster class
# ------------------------------------------------------------------------------------------------ #


class Player(UserMixin):
    def __init__(self, name):
        self.name = name
        self.sid = request.sid
        self.role = None
        self.dead = False
        self.mayor = False
        self._info = {}

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

    @property
    def teams(self):
        if self.role:
            return [self.role.team]

    @property
    def info(self):
        for name, player in g.PLAYERS.items():
            if name not in self._info:
                self._info[name] = {'role': None, 'dead': False, 'other': []}
            if player.dead and 'dead' not in self._info[name]['other']:
                self._info[name]['dead'] = True
                self._info[name]['other'].remove('mayor')
            for team in [x for x in player.teams if x in self.teams]:
                if team == 'Geliefden' and 'lover' not in self._info[name]['other']:
                    self._info[name]['other'].append('lover')
                if team == "Nazi's" and not self._info[name]['role']:
                    self._info[name]['role'] = type(player.role).__name__
            if player.mayor and 'mayor' not in self._info[name]['other']:
                self._info[name]['other'].append('mayor')
        return self._info


class GameMaster(Player):
    def __init__(self):
        Player.__init__(self, None)
