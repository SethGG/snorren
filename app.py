from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send
from flask_login import LoginManager, UserMixin, current_user, login_user
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
login = LoginManager(app)
socketio = SocketIO(app)

# ------------------------------------------------------------------------------------------------ #
# Global variables
# ------------------------------------------------------------------------------------------------ #

GAME_IN_PROGRESS = False
CURRENT_PHASE = Lobby()
GAME_MASTER = None
PLAYERS = {}
ROLES = {
    'Burger': (0, 5),
    'Nazi': (1, 5),
    'Snor': (0, 1),
    'Herbergier': (1, 1),
    'Priester': (1, 1),
    'Hoer': (1, 1),
    'Pimp': (0, 1),
    'Scooterjeugd': (0, 1),
    'Oma': (0, 1)}

# ------------------------------------------------------------------------------------------------ #
# Player class
# ------------------------------------------------------------------------------------------------ #


class Player(UserMixin):
    def __init__(self, name):
        self.name = name
        self.sid = request.sid
        self.role = None
        self.page = lobby_page(gm=(not bool(name)))

    def get_id(self):
        return self.sid

    @property
    def current_page(self):
        return CURRENT_PHASE.render_page(self.role)

    @property
    def is_active(self):
        return bool(self.sid)

    @is_active.setter
    def is_active(self, bool):
        if bool and not self.sid:
            self.sid = request.sid
        elif not bool:
            self.sid = None


class GameMaster(Player):
    def __init__(self):
        Player.__init__(self, None)
        self.role = 'game master'


@login.user_loader
def load_user(id):
    return [player for player in [GAME_MASTER] + list(PLAYERS.values()) if player.sid == id][0]


# ------------------------------------------------------------------------------------------------ #
# Index route
# ------------------------------------------------------------------------------------------------ #


@app.route("/")
def index():
    return render_template("index.html")

# ------------------------------------------------------------------------------------------------ #
# SocketIO event handlers
# ------------------------------------------------------------------------------------------------ #


@socketio.on('join')
def handle_join(msg):
    def handle_player(name):
        if GAME_IN_PROGRESS:
            if name not in PLAYERS:
                send('Er is nog een spel bezig')
            elif not PLAYERS[name].is_active:
                login_user(PLAYERS[name])
                emit('update_page')
        elif name in PLAYERS:
            send('Deze naam is al in gebruik')
        else:
            PLAYERS[name] = Player(name)
            login_user(PLAYERS[name])
            emit('update_users', {'users': list(PLAYERS)}, broadcast=True)
            emit('update_page')

    def handle_game_master():
        global GAME_MASTER
        if GAME_IN_PROGRESS:
            if GAME_MASTER.is_active:
                send('Er is nog een spel bezig')
            else:
                login_user(GAME_MASTER)
                emit('update_page')
        elif GAME_MASTER:
            send('Er heeft zich al een spelleider aangeboden.')
        else:
            GAME_MASTER = Player()
            login_user(GAME_MASTER)
            emit('update_page')

    if current_user.is_authenticated:
        send('Je bent al ingelogd')
    elif type(msg) is dict and 'type' in msg:
        if msg['type'] == 'game master':
            handle_game_master()
        elif msg['type'] == 'player' and 'name' in msg and type(msg['name']) is str:
            handle_player(msg['name'])


@socketio.on('disconnect')
def handle_disconnect():
    global GAME_MASTER
    if not GAME_IN_PROGRESS:
        if current_user == GAME_MASTER:
            GAME_MASTER = None
        elif current_user in PLAYERS.values():
            del PLAYERS[current_user.name]


@socketio.on('request_page')
def handle_request_page():
    if current_user.is_authenticated:
        emit('receive_page', current_user.page)


# ------------------------------------------------------------------------------------------------ #
# Lobby namespace
# ------------------------------------------------------------------------------------------------ #


@socketio.on('request_users')
def handle_request_users():
    emit('update_users', {'users': list(PLAYERS)})


@socketio.on('start_game')
def handle_start_game(roles):
    global GAME_IN_PROGRESS
    if not GAME_IN_PROGRESS and current_user == GAME_MASTER:
        pool = []
        error = False
        for role, tuple in ROLES.items():
            if role not in roles:
                send('Aantal "%s" is niet opgegeven.' % role, namespace='/')
                error = True
            elif tuple[0] <= roles[role] <= tuple[1]:
                pool.extend([role] * roles[role])
            else:
                send('Opgegeven aantal "%s" is illegaal.' % role, namespace='/')
                error = True

        if len(pool) != len(PLAYERS):
            send('Opgegeven aantal rollen is ongelijk aan het aantal spelers.', namespace='/')
            error = True

        if not error:
            GAME_IN_PROGRESS = True
            random.shuffle(pool)
            for idx, player in enumerate(PLAYERS.values()):
                player.role = pool[idx]

            print(PLAYERS)


# ------------------------------------------------------------------------------------------------ #
# Game master events
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
# Page creation functions
# ------------------------------------------------------------------------------------------------ #


def lobby_page(gm):
    return render_template("lobby.html", gm=gm, roles=ROLES)


def day_page(day_num):
    return render_template("day.html", day_num=day_num)


def night_page(night_num):
    return render_template("night.html", night_num=night_num)

# ------------------------------------------------------------------------------------------------ #
# Day cycle functions
# ------------------------------------------------------------------------------------------------ #


def day_cycle_factory():
    def day_start():
        pass

    def day_burgermeester():
        pass

    def day_discussie():
        pass

    def day_dorpsraad():
        pass

    def day_priester():
        pass

    def day_end():
        pass


# ------------------------------------------------------------------------------------------------ #
# Night cycle functions
# ------------------------------------------------------------------------------------------------ #

def night_cycle_factory():
    def night_start():
        print("yeet")

    def night_priester():
        print("yeet2")

    def night_herbergier():
        print("yeet3")

    def night_hoer():
        print("yeet4")

    def night_pimp():
        print("yeet5")

    def night_scooterjeugd():
        print("yeet6")

    def night_snor():
        print("yeet7")

    def night_nazis():
        print("yeet8")

    return [night_start, night_priester]
