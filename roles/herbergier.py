from basephase import BasePhase
from flask_login import current_user
from flask_socketio import emit, send
from flask import render_template
from cerberus import Validator
from roles.burger import Burger


class NightStep(BasePhase):

    name = 'NachtHerbergier'
    priority = 2

    def __init__(self, manager):
        super().__init__(manager)
        self.used = False

    def send_page(self, player=current_user):
        emit('update_page',
             render_template('game/night_herbergier.html', num=self.parent.num, player=player),
             room=player.sid)

    def handle_message(self, msg):
        schema = {
            'request': {
                'type': 'string',
                'allowed': ['reveal']
            },
            'name': {
                'type': 'string',
                'allowed': [x for x, y in self.manager.players.items() if not y.dead]
            }
        }
        v = Validator(schema)
        if (v.validate(msg) and current_user.role.__class__.__name__ == 'Herbergier'
                and not self.used):
            role = self.manager.players[msg['name']].role.__class__.__name__
            current_user.info[msg['name']]['role'] = role
            send({'name': msg['name'], 'role': role})
            self.used = True
#            app.socketio.sleep(5)
            self.parent.start_next_phase()


class Herbergier(Burger):
    night_step = NightStep
