from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_login import LoginManager
from phases import Lobby
import globals as g

app = Flask(__name__)
login = LoginManager(app)
socketio = SocketIO(app)

g.CURRENT_PHASE = Lobby

# ------------------------------------------------------------------------------------------------ #
# User loader
# ------------------------------------------------------------------------------------------------ #


@login.user_loader
def load_user(id):
    all_playes = list(g.PLAYERS.values()) + \
        [g.GAME_MASTER] if g.GAME_MASTER else list(g.PLAYERS.values())
    return [player for player in all_playes if player.sid == id][0]

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
    g.CURRENT_PHASE.handle_join(msg)


@socketio.on('disconnect')
def handle_disconnect():
    g.CURRENT_PHASE.handle_disconnect()


@socketio.on('message')
def handle_message(msg):
    g.CURRENT_PHASE.handle_message(msg)
