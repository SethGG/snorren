from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# ------------------------------------------------------------------------------------------------ #

GAME_IN_PROGRESS = False
GAME_MASTER = None
PLAYERS = {}

# ------------------------------------------------------------------------------------------------ #


@app.route("/")
def index():
    return render_template("index.html")

# ------------------------------------------------------------------------------------------------ #


@socketio.on('new_payer')
def handle_new_player(name):
    if name:
        if name in PLAYERS.keys():
            send('Deze naam is al in gebruik.')
        else:
            PLAYERS[name] = {'sid': request.sid}
            serve_page()
            emit('update_users', {'users': list(PLAYERS.keys())}, broadcast=True)


@socketio.on('new_game_master')
def handle_new_game_master():
    global GAME_MASTER
    if GAME_MASTER:
        send('Er heeft zich al een spelleider aangeboden.')
    else:
        GAME_MASTER = request.sid
        serve_page()
        emit('update_users', {'users': list(PLAYERS.keys())})


@socketio.on('disconnect')
def handle_disconnect():
    if not GAME_IN_PROGRESS:
        global GAME_MASTER
        if request.sid == GAME_MASTER:
            GAME_MASTER = None
        else:
            for name in [name for name, data in PLAYERS.items() if data['sid'] == request.sid]:
                del PLAYERS[name]
                emit('update_users', {'users': list(PLAYERS.keys())}, broadcast=True)

# ------------------------------------------------------------------------------------------------ #


def serve_page():
    if not GAME_IN_PROGRESS:
        if request.sid == GAME_MASTER:
            emit('reload_page', render_template("lobby.html", gm=True))
        else:
            emit('reload_page', render_template("lobby.html", gm=False))


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
