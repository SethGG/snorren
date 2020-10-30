from basephase import BasePhase
from roles.burger import Burger
from flask_socketio import emit
from flask_login import current_user
from flask import render_template
from cerberus import Validator


class NightStep(BasePhase):
    name = 'NachtPimp'
    priority = 4

    def __init__(self, parent):
        super().__init__(parent)

    def send_page(self, player=current_user):
        emit('update_page',
             render_template('game/night_pimp.html', num=self.parent.num, player=player),
             room=player.sid)

    def handle_message(self, msg):
        schema = {
            'request': {
                'type': 'string',
                'allowed': ['move hoer', 'dont smile', 'continue']
            },
            'name': {
                'type': 'string',
                'required': False,
                'dependencies': {'request': ['move hoer']},
                'allowed': [x for x, y in self.manager.players.items() if not y.dead]
            }
        }
        v = Validator(schema)
        if v.validate(msg) and current_user.role.__class__.__name__ == 'Pimp':
            if msg['request'] == 'move hoer' and current_user.role.move_hoer:
                if 'hoer' in self.parent.protected:
                    self.parent.protected['hoer'] = [msg['name']]
                current_user.role.move_hoer = False
            elif msg['request'] == 'dont smile' and current_user.role.dont_smile:
                self.parent.protected['pimp'] = [current_user.name]
                current_user.role.dont_smile = False
            elif msg['request'] == 'continue':
                self.parent.start_next_phase()


class Pimp(Burger):
    name = "Pimp"
    night_step = NightStep

    def __init__(self):
        self._move_hoer = True
        self.dont_smile = True

    @property
    def move_hoer(self):
        if 'Hoer' in [x.role.__class__.__name__ for x in self.manager.players.values()]:
            return self._move_hoer
        else:
            return False

    @move_hoer.setter
    def move_hoer(self, bool):
        self._move_hoer = bool
