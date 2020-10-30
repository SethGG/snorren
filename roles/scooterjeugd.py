from basephase import BasePhase
from roles.burger import Burger
from flask_socketio import emit
from flask_login import current_user
from flask import render_template
from cerberus import Validator


class NightStep(BasePhase):
    name = 'NachtScooterjeugd'
    priority = 5

    def __init__(self, parent):
        super().__init__(parent)

    def send_page(self, player=current_user):
        emit('update_page',
             render_template('game/night_scooter.html', num=self.parent.num, player=player),
             room=player.sid)

    def handle_message(self, msg):
        schema = {
            'request': {
                'type': 'string',
                'allowed': ['disturb night', 'continue']
            }
        }
        v = Validator(schema)
        if (v.validate(msg) and current_user.role.__class__.__name__ == 'Scooterjeugd'):
            if msg['request'] == 'disturb night' and current_user.role.disturb:
                self.parent.protected['Scooterjeugd'] = list(self.manager.players.keys())
                current_user.role.disturb = False
            if msg['request'] == 'continue':
                self.parent.start_next_phase()


class Scooterjeugd(Burger):
    name = "Scooterjeugd"
    night_step = NightStep

    def __init__(self):
        self.disturb = True
