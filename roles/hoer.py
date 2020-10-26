from basephase import BasePhase
from roles.burger import Burger
from flask_socketio import emit
from flask_login import current_user
from flask import render_template
from cerberus import Validator


class NightStep(BasePhase):

    name = 'NachtHoer'
    priority = 3

    def __init__(self, manager):
        super().__init__(manager)

    def send_page(self, player=current_user):
        emit('update_page',
             render_template('game/night_hoer.html', num=self.parent.num, player=player),
             room=player.sid)

    def handle_message(self, msg):
        schema = {
            'request': {
                'type': 'string',
                'allowed': ['protect']
            },
            'name': {
                'type': 'string',
                'allowed': [x for x, y in self.manager.players.items() if not y.dead]
            }
        }
        v = Validator(schema)
        if (v.validate(msg) and current_user.role.__class__.__name__ == 'Hoer'):
            self.parent.protected['hoer'] = [msg['name']]
            self.parent.start_next_phase()


class Hoer(Burger):
    night_step = NightStep
