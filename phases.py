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
                send({'error': 'Er is nog een spel bezig.\n\
                      Als je deelnemer was van dit spel kan je weer \
                      meedoen door aan te melden onder dezelfde naam.'})

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
        if current_user != g.GAME_MASTER:
            send({'error': '%s heeft het spel verlaten.' % current_user.name},
                 room=g.GAME_MASTER.sid)


class Night:

    steps = []

    class NightStart(BasePhase):
        def __init__(self, parent):
            super().__init__(parent)

        def send_page(self, player=current_user):
            emit('update_page', render_template('night.html', player=player), room=player.sid)

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


# class DayNightBase:
#     steps = None
#
#     def handle_join(self, msg):
#         def handle_player(name):
#             if name in g.PLAYERS and not g.PLAYERS[name].is_active:
#                 g.PLAYERS[name].is_active = True
#                 login_user(g.PLAYERS[name])
#                 self.send_page()
#
#         def handle_game_master():
#             if not g.GAME_MASTER.is_active:
#                 g.GAME_MASTER.is_active = True
#                 login_user(g.GAME_MASTER)
#                 self.send_page()
#
#         schema = {
#             'type': {
#                 'type': 'string',
#                 'allowed': ['game master', 'player']
#             },
#             'name': {
#                 'type': 'string',
#                 'required': False,
#                 'dependencies': {'type': ['player']}
#             }
#         }
#         v = Validator(schema)
#         if v.validate(msg) and not current_user.is_authenticated:
#             if msg['type'] == 'game master':
#                 handle_game_master()
#             elif msg['type'] == 'player':
#                 handle_player(msg['name'])
#
#     @staticmethod
#     def handle_disconnect():
#         current_user.is_active = False
#
#     def send_page(self, player=current_user):
#         emit('update_page', render_template(self.steps[0].template, player=player), room=player.sid)
#
#
# class Night(DayNightBase):
#     class NightStart:
#         def send_page(player=current_user):
#             emit('update_page', render_template('night.html', player=player), room=player.sid)
#
#         def handle_message(msg):
#             pass
#
#     class NightEnd:
#         def send_page(player=current_user):
#             emit('update_page', render_template('night.html', player=player), room=player.sid)
#
#         def handle_message(msg):
#             pass
#
#     def __init__(self, num):
#         def get_prio(step):
#             return step.priority
#
#         self.num = num
#         if not Night.steps:
#             Night.steps = sorted({player.role.night_step for player in g.PLAYERS.values()
#                                   if player.role.night_step}, key=get_prio)
#
#         for player in [g.GAME_MASTER] + list(g.PLAYERS.values()):
#             self.steps[0].send_page(player)
#
#     def start_next_step(self):
#         del self.steps[0]
#         if self.steps:
#             for player in [g.GAME_MASTER] + list(g.PLAYERS.values()):
#                 self.steps[0].send_page(player)
#         else:
#             g.CURRENT_PHASE = Day(self.num)
#
#
# class Day(DayNightBase):
#     def __init__(self, num):
#         def get_prio(step):
#             return step.priority
#
#         self.num = num
#         if not Day.steps:
#             Day.steps = sorted({player.role.day_step for player in g.PLAYERS.values()
#                                 if player.role.day_step}, key=get_prio)
#
#     def start_next_step(self):
#         del self.steps[0]
#         if not self.steps:
#             g.CURRENT_PHASE = Night(self.num + 1)
