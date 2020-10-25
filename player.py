from flask import request
from flask_login import UserMixin
import globals as g

# ------------------------------------------------------------------------------------------------ #
# Player and GameMaster class
# ------------------------------------------------------------------------------------------------ #


class BaseUser(UserMixin):
    def __init__(self):
        self.sid = request.sid

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


class Player(BaseUser):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.role = None
        self.dead = False
        self.lover = False
        self.mayor = False
        self._info = {}

    @property
    def teams(self):
        if self.role:
            if self.lover:
                return [self.role.team, 'Geliefden']
            else:
                return [self.role.team]

    @property
    def info(self):
        for name, player in g.PLAYERS.items():
            if name not in self._info:
                self._info[name] = {'role': None, 'dead': False, 'other': []}
            if name == self.name:
                self._info[name]['role'] = type(self.role).__name__
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


class GameMaster(BaseUser):
    def __init__(self):
        super().__init__()

    @property
    def info(self):
        info = {}
        for name, player in g.PLAYERS.items():
            info[name] = {
                'role': type(player.role).__name__,
                'dead': player.dead,
                'other': []
            }
            if 'Geliefden' in player.teams:
                info[name]['other'].append('lover')
            if player.mayor:
                info[name]['other'].append('mayor')
        return info
