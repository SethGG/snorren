from logging import getLogger, StreamHandler, Formatter
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_login import LoginManager
from roles import roles
from player import Player
from random import shuffle
from lobby import Lobby


class Snorren():
    roles = roles

    def __init__(self, debug='NOTSET'):
        # Setup Flask app
        self.app = Flask(__name__)
        @self.app.route("/")
        def index():
            return render_template("index.html")
        # Setup SocketIO
        self.socketio = SocketIO(self.app)
        # Setup Login Manager
        self.login = LoginManager(self.app)
        @self.login.user_loader
        def load_user(id):
            return next(p for p in self.players if p.sid == id)
        # Setup Logger
        self.logger = getLogger(str(hex(id(self))))
        self.logger.setLevel(debug)
        self.handler = StreamHandler()
        self.formatter = Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        # Setup initial game state
        self.reset_game()

    def reset_game(self):
        self.players = {}
        self.current_phase = Lobby()
        self.game_loop = None

    def connect_player(self, name, sid):
        if self.game_loop:
            if name in self.players and not self.players[name].is_active:
                self.players[name].sid = sid
                return self.players[name]
            else:
                raise RuntimeError('Er is nog een spel bezig. Probeer later opnieuw.')
        else:
            if name in self.players:
                raise ValueError('De naam %s is al in gebruik.' % name)
            else:
                player = Player(name=name, sid=sid, game=self)
                self.players[name] = player
                return player

    def disconnect_player(self, name):
        if self.game_loop:
            if name in self.players:
                self.players[name].sid = None
        else:
            if name in self.players:
                del self.players[name]

    def start_game(self, role_selection):
        if self.game_loop:
            raise RuntimeError('Er is al een spel bezig.')
        if not self.players:
            raise RuntimeError('Er zijn geen spelers aangemeld')
        roles = {r: role_selection[r.name] for r in self.roles if r.name in role_selection}
        for role, count in roles.items():
            if count < self.roles[role][0] or count > self.roles[role][1]:
                raise ValueError('Het opgegeven aantal voor de rol %s is niet toegestaan. '
                                 '(Opgegeven: %d, Toegestaan: %d-%d)'
                                 % (role.name, count, self.roles[role][0], self.roles[role][1]))
        if len(self.players) != sum(roles.values()):
            raise ValueError('Opgegeven aantal rollen ongelijk aan het aantal spelers. '
                             '(Opgegeven: %d, Aantal spelers: %d)'
                             % (sum(roles.values()), len(self.players)))
        role_pool = []
        for role, count in roles.items():
            role_pool.extend([role()] * count)
        shuffle(role_pool)
        for i, player in enumerate(self.players.values()):
            player.role = role_pool[0]
        self.game_loop = self.generate_game_loop()
        self.start_next_phase()

    def generate_game_loop(self):
        while any(p.roles for p in self.players):
            yield None

    def start_next_phase(self):
        if self.game_loop:
            self.current_phase = next(self.game_loop)

    def run_server(self, **kwargs):
        self.socketio.run(self.app, **kwargs)
