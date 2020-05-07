from flask import render_template
from flask_socketio import send, emit
from flask_login import current_user
from cerberus import Validator
from phases import BasePhase
import globals as g
import app


class Burger:
    team = "Burgers"
    night_step = None
    day_step = None
    death_step = None


class Herbergier(Burger):
    class night_step(BasePhase):
        priority = 1

        def __init__(self, parent):
            super().__init__(parent)
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
                    'allowed': [x for x, y in g.PLAYERS.items() if not y.dead]
                }
            }
            v = Validator(schema)
            if (v.validate(msg) and current_user.role.__class__.__name__ == 'Herbergier'
                    and not self.used):
                role = g.PLAYERS[msg['name']].role.__class__.__name__
                current_user.info[msg['name']]['role'] = role
                send({'name': msg['name'], 'role': role})
                self.used = True
                app.socketio.sleep(5)
                self.parent.start_next_phase()


class Hoer(Burger):
    class night_step(BasePhase):
        priority = 2

        def __init__(self, parent):
            super().__init__(parent)

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
                    'allowed': [x for x, y in g.PLAYERS.items() if not y.dead]
                }
            }
            v = Validator(schema)
            if (v.validate(msg) and current_user.role.__class__.__name__ == 'Hoer'):
                self.parent.protected.append(msg['name'])
                self.parent.start_next_phase()


class Oma(Burger):
    def __init__(self):
        Burger.__init__(self)


class Pimp(Burger):
    def __init__(self):
        Burger.__init__(self)


class Priester(Burger):
    def __init__(self):
        Burger.__init__(self)


class Scooterjeugd(Burger):
    def __init__(self):
        Burger.__init__(self)


class Nazi:
    team = "Nazi's"
    night_step = None
    day_step = None
    death_step = None


class Snor(Nazi):
    def __init__(self):
        Nazi.__init__(self)
