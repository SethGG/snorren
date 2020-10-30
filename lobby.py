from flask_socketio import send
from flask_login import current_user, login_user
from cerberus import Validator
from player import Player, GameMaster
from basephase import BasePhase


class Lobby(BasePhase):
    name = 'Lobby'
    page_path = 'lobby/lobby.html'

    def __init__(self, game):
        super().__init__(game)

    def handle_player(self, name):
        if name in [x.name for x in self.game.players]:
            send({'error': 'Deze naam is al in gebruik'})
        else:
            player = Player(self.game, name)
            self.game.players.append(player)
            login_user(player)
            self.send_page()
            send({'users': [x.name for x in self.game.players]}, broadcast=True)
            print('Nieuwe speler aangemeld: %s' % name)

    def handle_game_master(self):
        if self.game.game_master:
            send({'error': 'Er heeft zich al een spelleider aangeboden.'})
        else:
            self.game.game_master = GameMaster(self.game)
            login_user(self.game.game_master)
            self.send_page()
            send({'users': [x.name for x in self.game.players]})
            print('Nieuwe spelleider aangemeld')

    def handle_join(self, msg):
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
                self.handle_game_master()
            elif msg['type'] == 'player':
                self.handle_player(msg['name'])

    # def start_game(role_selection):
    #     pool = []
    #     for role, num in role_selection.items():
    #         obj = [x for x in self.game.roles if x.__name__ == role]
    #         pool.extend(obj * num)
    #     if len(pool) != len(self.game.players):
    #         send({'error': 'Opgegeven aantal rollen is ongelijk aan het aantal spelers.'})
    #     else:
    #         random.shuffle(pool)
    #         for idx, player in enumerate(self.game.players.values()):
    #             player.role = pool[idx]()
    #         Night(num=1)

    def handle_message(self, msg):
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
        for role, (min, max) in self.game.roles.items():
            schema['role_selection']['schema'][role.__name__] = {
                'type': 'integer', 'min': min, 'max': max}
        v = Validator(schema)
        if v.validate(msg) and current_user == self.game.game_master:
            self.game.start_game(msg['role_selection'])

    def handle_disconnect(self):
        if current_user == self.game.game_master:
            self.game.game_master = None
            print('Spelleider heeft zich afgemeld')
        elif current_user in self.game.players:
            self.game.players.remove(current_user)
            send({'users': [x.name for x in self.game.players]}, broadcast=True)
            print('Speler heeft zich afgemeld: %s' % current_user.name)
