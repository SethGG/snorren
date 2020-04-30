from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send
import random
from roles.burger import Burger
from roles.herbergier import Herbergier
from roles.hoer import Hoer
from roles.nazi import Nazi
from roles.oma import Oma
from roles.pimp import Pimp
from roles.priester import Priester
from roles.scooterjeugd import Scooterjeugd
from roles.snor import Snor


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# ------------------------------------------------------------------------------------------------ #
# Global variables
# ------------------------------------------------------------------------------------------------ #

GAME_IN_PROGRESS = False
GAME_MASTER = None
PLAYERS = {}
ROLES = {
    Burger: (0, 5),
    Nazi: (1, 5),
    Snor: (0, 1),
    Herbergier: (1, 1),
    Priester: (1, 1),
    Hoer: (1, 1),
    Pimp: (0, 1),
    Scooterjeugd: (0, 1),
    Oma: (0, 1)}
DAY_CYCLE = []
NIGHT_CYCLE = []

# ------------------------------------------------------------------------------------------------ #
# Index route
# ------------------------------------------------------------------------------------------------ #


@app.route("/")
def index():
    return render_template("index.html")

# ------------------------------------------------------------------------------------------------ #
# Connect and Disconect events
# ------------------------------------------------------------------------------------------------ #


@socketio.on('new_payer')
def handle_new_player(name):
    if name:
        if GAME_IN_PROGRESS and name not in [x['name'] for x in PLAYERS.values()]:
            send('Er is nog een spel bezig.')
        elif name in PLAYERS.keys() and not PLAYERS[name]['sid'] is None:
            send('Deze naam is al in gebruik.')
        elif request.sid in [data['sid'] for data in PLAYERS.values()]:
            send('Je bent al ingelogd onder een andere naam.')
        else:
            PLAYERS[name] = {'sid': request.sid, 'page': lobby_page(gm=False)}
            emit('update_users', {'users': list(PLAYERS.keys())}, broadcast=True)
            emit('update_page')


@socketio.on('new_game_master')
def handle_new_game_master():
    global GAME_MASTER
    if GAME_MASTER:
        send('Er heeft zich al een spelleider aangeboden.')
    elif request.sid in [data['sid'] for data in PLAYERS.values()]:
        send('Je bent al ingelogd als speler.')
    else:
        GAME_MASTER = {'sid': request.sid, 'page': lobby_page(gm=True)}
        emit('update_page')


@socketio.on('disconnect')
def handle_disconnect():
    global GAME_MASTER
    if GAME_MASTER and request.sid == GAME_MASTER['sid']:
        GAME_MASTER = None
    else:
        for name in [name for name, data in PLAYERS.items() if data['sid'] == request.sid]:
            if not GAME_IN_PROGRESS:
                del PLAYERS[name]
                emit('update_users', {'users': list(PLAYERS.keys())}, broadcast=True)
            else:
                PLAYERS[name]['sid'] = None

# ------------------------------------------------------------------------------------------------ #
# Request data events
# ------------------------------------------------------------------------------------------------ #


@socketio.on('request_users')
def handle_request_users():
    emit('update_users', {'users': list(PLAYERS.keys())})


@socketio.on('request_page')
def handle_request_page():
    if GAME_MASTER and request.sid == GAME_MASTER['sid']:
        emit('receive_page', GAME_MASTER['page'])
    else:
        for page in [data['page'] for data in PLAYERS.values() if data['sid'] == request.sid]:
            emit('receive_page', page)

# ------------------------------------------------------------------------------------------------ #
# Game master events
# ------------------------------------------------------------------------------------------------ #


@socketio.on('start_game')
def handle_start_game(roles):
    if not GAME_IN_PROGRESS and GAME_MASTER and request.sid == GAME_MASTER['sid']:
        pool = []
        error = False
        for role, tuple in ROLES.items():
            if role.__name__ not in roles:
                send('Aantal "%s" is niet opgegeven.' % role.__name__)
                error = True
            elif tuple[0] <= roles[role.__name__] <= tuple[1]:
                pool.extend([role()] * roles[role.__name__])
            else:
                send('Opgegeven aantal "%s" is illegaal.' % role.__name__)
                error = True

        if len(pool) != len(PLAYERS):
            send('Opgegeven aantal rollen is ongelijk aan het aantal spelers.')
            error = True

        if not error:
            random.shuffle(pool)
            for idx, data in enumerate(PLAYERS.values()):
                data['role'] = pool[idx]

            print(PLAYERS)

# ------------------------------------------------------------------------------------------------ #
# Page creation functions
# ------------------------------------------------------------------------------------------------ #


def lobby_page(gm):
    return render_template("lobby.html", gm=gm, roles=ROLES)
