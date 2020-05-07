from flask import render_template
from flask_socketio import send, emit
from flask_login import current_user, login_user
from cerberus import Validator
from player import Player, GameMaster
from phases import Night
import globals as g
import random


class Lobby:
    @staticmethod
    def handle_join(msg):
        def handle_player(name):
            if name in g.PLAYERS:
                send({'error': 'Deze naam is al in gebruik'})
            else:
                g.PLAYERS[name] = Player(name)
                login_user(g.PLAYERS[name])
                emit('update_page', render_template('lobby/lobby.html'))
                send({'users': list(g.PLAYERS)}, broadcast=True)

        def handle_game_master():
            if g.GAME_MASTER:
                send({'error': 'Er heeft zich al een spelleider aangeboden.'})
            else:
                g.GAME_MASTER = GameMaster()
                login_user(g.GAME_MASTER)
                emit('update_page', render_template('lobby/lobby.html', gm=True, roles=g.ROLES))
                send({'users': list(g.PLAYERS)})

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
                obj = [x for x in g.ROLES if x.__name__ == role]
                pool.extend(obj * num)
            if len(pool) != len(g.PLAYERS):
                send({'error': 'Opgegeven aantal rollen is ongelijk aan het aantal spelers.'})
            else:
                random.shuffle(pool)
                for idx, player in enumerate(g.PLAYERS.values()):
                    player.role = pool[idx]()
                Night(num=1)

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
            schema['role_selection']['schema'][role.__name__] = {
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
