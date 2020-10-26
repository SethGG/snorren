from basephase import BasePhase
from roles.burger import Burger
from flask_socketio import emit
from flask_login import current_user
from flask import render_template
from cerberus import Validator


class NightStep(BasePhase):
    name = 'NachtPriester'
    priority = 1

    def __init__(self, parent):
        if not parent.num == 1:
            parent.start_next_phase()
        super().__init__(parent)

    def send_page(self, player=current_user):
        emit('update_page',
             render_template('game/night_priester.html', num=self.parent.num, player=player),
             room=player.sid)

    def handle_message(self, msg):
        schema = {
            'request': {
                'type': 'string',
                'allowed': ['match']
            },
            'names': {
                'type': 'list',
                'schema': {
                    'type': 'string',
                    'allowed': [x for x, y in self.manager.players.items() if not y.dead]
                },
                'minlength': 2,
                'maxlength': 2
            }
        }
        v = Validator(schema)
        if (v.validate(msg) and current_user.role.__class__.__name__ == 'Priester'):
            for name in msg['names']:
                self.manager.players[name].lover = True
            self.parent.start_next_phase()


class Priester(Burger):
    night_step = NightStep
