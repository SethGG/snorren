from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_login import LoginManager
from manager import Manager

app = Flask(__name__)
login = LoginManager(app)
socketio = SocketIO(app)
manager = Manager()

# ------------------------------------------------------------------------------------------------ #
# User loader
# ------------------------------------------------------------------------------------------------ #


@login.user_loader
def load_user(id):
    return [p for p in manager.players + [manager.game_master] if p and p.sid == id][0]

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
    manager.current_phase.handle_join(msg)


@socketio.on('disconnect')
def handle_disconnect():
    manager.current_phase.handle_disconnect()


@socketio.on('message')
def handle_message(msg):
    manager.current_phase.handle_message(msg)
