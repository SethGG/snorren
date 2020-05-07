from flask import render_template
from flask_socketio import emit
from flask_login import current_user
from phases import BasePhase


class Burger:
    team = "Burgers"
    night_step = None
    day_step = None
    death_step = None


class Herbergier(Burger):
    class night_step(BasePhase):
        priority = 1

        def __init__(self, parent):
            super().__init__(parent)

        def send_page(self, player=current_user):
            emit('update_page',
                 render_template('game/night_herbergier.html', num=self.parent.num, player=player),
                 room=player.sid)

        def handle_message(self, msg):
            print(msg)


class Hoer(Burger):
    def __init__(self):
        Burger.__init__(self)


class Oma(Burger):
    def __init__(self):
        Burger.__init__(self)


class Pimp(Burger):
    def __init__(self):
        Burger.__init__(self)


class Priester(Burger):
    def __init__(self):
        Burger.__init__(self)


class Scooterjeugd(Burger):
    def __init__(self):
        Burger.__init__(self)


class Nazi:
    team = "Nazi's"
    night_step = None
    day_step = None
    death_step = None


class Snor(Nazi):
    def __init__(self):
        Nazi.__init__(self)
