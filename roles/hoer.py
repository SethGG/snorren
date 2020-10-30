from basephase import BasePhase
from roles.burger import Burger
from flask_login import current_user
from cerberus import Validator


class NightStep(BasePhase):
    name = 'NachtHoer'
    page_path = 'game/night_hoer.html'
    priority = 3

    def __init__(self, manager):
        super().__init__(manager)

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
    name = "Hoer"
    night_step = NightStep
