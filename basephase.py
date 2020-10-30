from flask_socketio import send, emit
from flask_login import current_user, login_user
from flask import render_template
from cerberus import Validator


class BasePhase:
    def __init__(self, game):
        self.game = game
        self.game.logger.info('Nieuwe fase begonnen: %s' % self.name)

        @game.socketio.on('join')
        def handle_join(msg):
            self.handle_join(msg)

        @game.socketio.on('disconnect')
        def handle_disconnect():
            self.handle_disconnect()

        @game.socketio.on('message')
        def handle_message(msg):
            self.handle_message(msg)

        for player in (p for p in game.players + [game.game_master] if p):
            self.send_page(player=player)

    def send_page(self, player=current_user):
        emit('update_page', render_template(self.page_path, player=player), room=player.sid)

    def handle_player(self, name):
        for player in (p for p in self.game.players if p.name == name and not p.is_active):
            player.is_active = True
            login_user(player)
            self.send_page()
            print('Speler heeft zich opnieuw aangemeld: %s' % name)
            break
        else:
            send({'error': 'Er is nog een spel bezig.\n'
                  'Als je deelnemer was van dit spel kan je weer\n'
                  'meedoen door aan te melden met dezelfde naam.'})

    def handle_game_master(self):
        if not self.game.game_master.is_active:
            self.game.game_master.is_active = True
            login_user(self.game.game_master)
            self.send_page()
            print('Spelleider heeft zich opnieuw aangemeld')
        else:
            send({'error': 'Er is nog een spel bezig met een actieve spelleider.'})

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
                self.handle_game_master(self)
            elif msg['type'] == 'player':
                self.handle_player(self, msg['name'])

    def handle_message(self, msg):
        schema = {
            'request': {
                'type': 'string',
                'allowed': ['continue']
            }
        }
        v = Validator(schema)
        if v.validate(msg) and current_user == self.game.game_master:
            self.parent.start_next_phase()

    def handle_disconnect(self):
        if current_user.is_authenticated:
            if current_user == self.game.game_master:
                print('Connectie met spelleider verbroken')
            else:
                print('Connectie met speler verbroken: %s' % current_user.name)
            current_user.is_active = False
