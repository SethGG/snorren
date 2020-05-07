from flask import render_template
from flask_socketio import send, emit
from flask_login import current_user, login_user
from cerberus import Validator
import globals as g


class BasePhase:
    def __init__(self, parent):
        self.parent = parent
        for player in [g.GAME_MASTER] + list(g.PLAYERS.values()):
            self.send_page(player)

    def handle_join(self, msg):
        def handle_player(name):
            if name in g.PLAYERS and not g.PLAYERS[name].is_active:
                g.PLAYERS[name].is_active = True
                login_user(g.PLAYERS[name])
                self.send_page()
            else:
                send({'error': 'Er is nog een spel bezig.\n'
                      'Als je deelnemer was van dit spel kan je weer\n'
                      'meedoen door aan te melden met dezelfde naam.'})

        def handle_game_master():
            if not g.GAME_MASTER.is_active:
                g.GAME_MASTER.is_active = True
                login_user(g.GAME_MASTER)
                self.send_page()
            else:
                send({'error': 'Er is nog een spel bezig met een actieve spelleider.'})

        schema = {
            'type': {
                'type': 'string',
                'allowed': ['game master', 'player']
            },
            'name': {
                'type': 'string',
                'required': False,
                'dependencies': {'type': ['player']}
            }
        }
        v = Validator(schema)
        if v.validate(msg) and not current_user.is_authenticated:
            if msg['type'] == 'game master':
                handle_game_master()
            elif msg['type'] == 'player':
                handle_player(msg['name'])

    def handle_message(self, msg):
        schema = {
            'request': {
                'type': 'string',
                'allowed': ['continue']
            }
        }
        v = Validator(schema)
        if v.validate(msg) and current_user == g.GAME_MASTER:
            self.parent.start_next_phase()

    @staticmethod
    def handle_disconnect():
        current_user.is_active = False


class Night:

    steps = []

    class NightStart(BasePhase):
        def __init__(self, parent):
            super().__init__(parent)

        def send_page(self, player=current_user):
            emit('update_page',
                 render_template('game/night_start.html', num=self.parent.num, player=player),
                 room=player.sid)

    class NightEnd(BasePhase):
        def __init__(self, parent):
            super().__init__(parent)

        def send_page(self, player=current_user):
            emit('update_page', render_template('night.html', player=player), room=player.sid)

    def __init__(self, num):
        def get_prio(step):
            return step.priority

        self.num = num
        if not Night.steps:
            Night.steps = sorted({player.role.night_step for player in g.PLAYERS.values()
                                  if player.role.night_step}, key=get_prio)
            Night.steps = [self.NightStart] + Night.steps + [self.NightEnd]

        g.CURRENT_PHASE = self.steps[0](self)

    def start_next_phase(self):
        del self.steps[0]
        g.CURRENT_PHASE = self.steps[0](self)
