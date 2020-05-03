from flask import render_template
from flask_socketio import send, emit
from flask_login import current_user, login_user
from cerberus import Validator
from player import Player, GameMaster
import globals as g
import random


class Lobby:
    @staticmethod
    def handle_join(msg):
        def send_page(gm=False):
            emit('update_page', render_template('lobby.html', gm=gm, roles=g.ROLES))
            send({'users': list(g.PLAYERS)}, broadcast=True)

        def handle_player(name):
            if name in g.PLAYERS:
                send({'error': 'Deze naam is al in gebruik'})
            else:
                g.PLAYERS[name] = Player(name)
                login_user(g.PLAYERS[name])
                send_page()

        def handle_game_master():
            if g.GAME_MASTER:
                send({'error': 'Er heeft zich al een spelleider aangeboden.'})
            else:
                g.GAME_MASTER = GameMaster()
                login_user(g.GAME_MASTER)
                send_page(gm=True)

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

    @staticmethod
    def handle_message(msg):
        def start_game(role_selection):
            pool = []
            for role, num in role_selection.items():
                pool.extend([role] * num)
            if len(pool) != len(g.PLAYERS):
                send({'error': 'Opgegeven aantal rollen is ongelijk aan het aantal spelers.'})
            else:
                random.shuffle(pool)
                for idx, player in enumerate(g.PLAYERS.values()):
                    player.role = pool[idx]

                print(g.PLAYERS)

        schema = {
            'request': {
                'type': 'string',
                'allowed': ['start game']
            },
            'role_selection': {
                'type': 'dict',
                'schema': {}
            }
        }
        for role, (min, max) in g.ROLES.items():
            schema['role_selection']['schema'][role] = {
                'type': 'integer', 'min': min, 'max': max}
        v = Validator(schema)
        if v.validate(msg) and current_user == g.GAME_MASTER:
            start_game(msg['role_selection'])

    @staticmethod
    def handle_disconnect():
        if current_user == g.GAME_MASTER:
            g.GAME_MASTER = None
        elif current_user in g.PLAYERS.values():
            del g.PLAYERS[current_user.name]
            send({'users': list(g.PLAYERS)}, broadcast=True)
