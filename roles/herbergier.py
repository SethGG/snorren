from basephase import BasePhase
from flask_login import current_user
from flask_socketio import send
from cerberus import Validator
from roles.burger import Burger


class NightStep(BasePhase):
    name = 'NachtHerbergier'
    page_path = 'game/night_herbergier.html'
    priority = 2

    def __init__(self, manager):
        super().__init__(manager)
        self.used = False

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
        if (v.validate(msg) and current_user.role.name == 'Herbergier' and not self.used):
            role = next(p.role.name for p in self.manager.players if p.name == msg['name'])
            current_user.info[msg['name']]['role'] = role
            send({'name': msg['name'], 'role': role})
            self.used = True
#            app.socketio.sleep(5)
            self.manager.start_next_phase()


class Herbergier(Burger):
    name = 'Herbergier'
    night_step = NightStep
