from basephase import BasePhase
from flask_socketio import emit, send
from flask_login import current_user
from flask import render_template
from cerberus import Validator


class night_step(BasePhase):
    name = 'NachtNazis'
    priority = 6

    def __init__(self, parent):
        super().__init__(parent)
        self.votes = {x: None for x, y in self.manager.players.items()
                      if not y.dead and "Nazi's" in y.teams}
        self.confirms = 0

    def send_page(self, player=current_user):
        emit('update_page',
             render_template('game/night_nazis.html', num=self.parent.num, player=player),
             room=player.sid)

    def handle_message(self, msg):
        schema = {
            'request': {
                'type': 'string',
                'allowed': ['vote', 'confirm', 'continue']
            },
            'name': {
                'type': 'string',
                'required': False,
                'dependencies': {'request': ['vote']},
                'allowed': [x for x, y in self.manager.players.items() if not y.dead]
            }
        }
        v = Validator(schema)
        if v.validate(msg) and "Nazi's" in current_user.teams:
            if msg['request'] == 'vote':
                self.votes[current_user.name] = msg['name']
                self.confirms = 0
                for name in self.votes:
                    if name != current_user.name:
                        send({current_user.name: msg['name']}, room=self.manager.players[name].sid)
            if msg['request'] == 'confirm':
                self.confirms += 1
                if self.confirms == len(self.votes):
                    self.parent.start_next_phase()


class Nazi:
    team = "Nazi's"
    day_step = None
    death_step = None
